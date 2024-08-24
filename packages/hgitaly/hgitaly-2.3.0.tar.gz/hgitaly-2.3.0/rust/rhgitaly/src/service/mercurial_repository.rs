// Copyright 2023 Georges Racinet <georges.racinet@octobus.net>
//
// This software may be used and distributed according to the terms of the
// GNU General Public License version 2 or any later version.
// SPDX-License-Identifier: GPL-2.0-or-later
use std::ffi::OsString;
use std::fmt::{Debug, Formatter};
use std::os::unix::ffi::OsStringExt;
use std::sync::Arc;
use tokio::sync::mpsc;
use tokio_util::sync::CancellationToken;
use tonic::{
    metadata::Ascii, metadata::MetadataMap, metadata::MetadataValue, Request, Response, Status,
};
use tracing::{info, instrument};
use url::Url;

use crate::config::Config;
use crate::gitaly::{Repository, User};
use crate::hgitaly::mercurial_repository_service_server::{
    MercurialRepositoryService, MercurialRepositoryServiceServer,
};
use crate::hgitaly::{MercurialPeer, PullRequest, PullResponse};
use crate::metadata::correlation_id;
use crate::repository::{
    default_repo_spec_error_status, HgSpawner, RequestHgSpawnable, RequestWithRepo,
};
use crate::util::tracing_span_id;

#[derive(Debug)]
pub struct MercurialRepositoryServiceImpl {
    config: Arc<Config>,
    shutdown_token: CancellationToken,
}

#[tonic::async_trait]
impl MercurialRepositoryService for MercurialRepositoryServiceImpl {
    async fn pull(&self, request: Request<PullRequest>) -> Result<Response<PullResponse>, Status> {
        let (metadata, _ext, inner) = request.into_parts();

        self.inner_pull(inner, correlation_id(&metadata), &metadata)
            .await
    }
}

impl MercurialRepositoryServiceImpl {
    #[instrument(name = "pull", skip(self, request))]
    async fn inner_pull(
        &self,
        request: PullRequest,
        correlation_id: Option<&MetadataValue<Ascii>>,
        metadata: &MetadataMap,
    ) -> Result<Response<PullResponse>, Status> {
        tracing_span_id!();
        info!("Processing, request={:?}", request);
        let config = self.config.clone();
        let mut spawner = HgSpawner::prepare(
            config,
            request.clone(),
            metadata,
            default_repo_spec_error_status,
        )
        .await?;
        let url = &request
            .remote_peer
            .as_ref()
            .ok_or(Status::invalid_argument("Missing remote peer"))?
            .url
            .clone();
        let mut args: Vec<OsString> = Vec::with_capacity(4 + request.mercurial_revisions.len() * 2);
        let allow_bookmarks = spawner
            .load_repo_and_then(move |repo| {
                repo.config()
                    .get_bool(b"heptapod", b"allow-bookmarks")
                    .map_err(|e| {
                        Status::internal(format!("Error reading repository config: {}", e))
                    })
            })
            .await?;
        info!("Allow bookmarks: {}", allow_bookmarks);

        if !allow_bookmarks {
            args.push("--config".into());
            args.push("heptapod.exchange-ignore-bookmarks=yes".into());
        };
        args.push("pull".to_owned().into());
        for revspec in &request.mercurial_revisions {
            args.push("-r".to_owned().into());
            args.push(OsString::from_vec(revspec.clone()));
        }
        args.push(url.into());
        // One can expect RHGitaly to read the hg stdout much faster than it will be produced,
        // hence we do not need a very large buffer
        let (stdout_tx, mut stdout_rx) = mpsc::channel(3);
        spawner.capture_stdout(stdout_tx);
        spawner.args(&args);
        let spawned = spawner.spawn(&self.shutdown_token);
        let read_stdout = async {
            let mut new_changesets = true;
            while let Some(line) = stdout_rx.recv().await {
                if line == "no changes found" {
                    new_changesets = false;
                }
            }
            new_changesets
        };
        let (spawn_result, new_changesets) = tokio::join!(spawned, read_stdout);
        let hg_exit_code = spawn_result?;
        if hg_exit_code != 0 {
            return Err(Status::internal(format!(
                "Mercurial subprocess exited with code {}",
                hg_exit_code
            )));
        }
        Ok(Response::new(PullResponse { new_changesets }))
    }
}

impl RequestWithRepo for PullRequest {
    fn repository_ref(&self) -> Option<&Repository> {
        self.repository.as_ref()
    }
}

impl RequestHgSpawnable for PullRequest {
    fn user_ref(&self) -> Option<&User> {
        self.user.as_ref()
    }
}

struct MercurialPeerTracing<'a>(&'a MercurialPeer);

impl<'a> Debug for MercurialPeerTracing<'a> {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        let mut parsed = Url::parse(&self.0.url);
        let stripped_url = match parsed {
            Ok(ref mut url) => {
                let _ignore_errors = url.set_password(None);
                url.as_str()
            }
            Err(_) => &self.0.url,
        };
        f.debug_struct("RemotePeer")
            .field("url", &stripped_url)
            .finish()
    }
}

struct PullTracingRequest<'a>(&'a PullRequest);

impl Debug for PullTracingRequest<'_> {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("PullRequest")
            .field("repository", &self.0.repository)
            .field(
                "remote_peer",
                &self.0.remote_peer.as_ref().map(MercurialPeerTracing),
            )
            .finish()
    }
}

/// Takes care of boilerplate that would instead be in the startup sequence.
pub fn mercurial_repository_server(
    config: &Arc<Config>,
    shutdown_token: &CancellationToken,
) -> MercurialRepositoryServiceServer<MercurialRepositoryServiceImpl> {
    MercurialRepositoryServiceServer::new(MercurialRepositoryServiceImpl {
        config: config.clone(),
        shutdown_token: shutdown_token.clone(),
    })
}
