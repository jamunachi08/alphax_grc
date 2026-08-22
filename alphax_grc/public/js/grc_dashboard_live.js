// AlphaX GRC v1.3.2 — Shared dashboard liveness module
// Provides a global frappe.alphaxGRC.live() helper that any dashboard page
// can use to wire up: 30s auto-refresh, realtime invalidation push, manual
// refresh button, and a "Live • updated Xs ago" indicator.
//
// Usage from a Frappe page on_page_load:
//   const live = frappe.alphaxGRC.live({
//       endpoint: 'alphax_grc.dashboards_live.get_live_dashboard',
//       getArgs: () => ({ client: CURRENT_CLIENT }),
//       onData: (payload) => render(payload),
//       indicatorEl: $page.find('.live-indicator'),
//       refreshSeconds: 30,
//   });
//   live.start();   // begins polling
//   // later: live.stop(), live.refreshNow(), live.setArgs(fn)

(function () {
    if (!window.frappe) return;
    frappe.alphaxGRC = frappe.alphaxGRC || {};

    const REALTIME_EVENT = 'grc.dashboard.refresh';
    const DEFAULT_REFRESH = 30;       // seconds
    const STALE_BADGE_AT = 60;        // seconds — turn indicator amber

    frappe.alphaxGRC.live = function (config) {
        const cfg = Object.assign({
            endpoint: null,                // required: server method
            getArgs: () => ({}),           // returns args object for frappe.call
            onData: () => {},              // called with the response payload
            onError: () => {},             // called on failure
            indicatorEl: null,             // jQuery or DOM node to update with status
            refreshSeconds: DEFAULT_REFRESH,
            pauseWhenHidden: true,         // skip polling when tab is hidden
            invalidateOnAnyClient: false,  // if true, refresh on any client's event
                                            // (used by firm-wide dashboards)
        }, config || {});

        if (!cfg.endpoint) {
            console.warn('alphaxGRC.live: endpoint is required');
            return null;
        }

        let timer = null;
        let lastFetchTime = null;
        let lastSnapshotTime = null;
        let isFetching = false;
        let currentArgs = cfg.getArgs;
        let started = false;
        let realtimeBound = false;

        function fetchOnce() {
            if (isFetching) return;
            isFetching = true;
            const args = (typeof currentArgs === 'function') ? currentArgs() : (currentArgs || {});
            frappe.call({
                method: cfg.endpoint,
                args: args,
                callback: (r) => {
                    isFetching = false;
                    if (r && r.message) {
                        lastFetchTime = new Date();
                        lastSnapshotTime = r.message.snapshot_time
                            ? new Date(r.message.snapshot_time)
                            : lastFetchTime;
                        try { cfg.onData(r.message); } catch (e) { console.error(e); }
                        updateIndicator();
                    }
                },
                error: (err) => {
                    isFetching = false;
                    try { cfg.onError(err); } catch (e) { console.error(e); }
                    updateIndicator(true);
                },
            });
        }

        function updateIndicator(isError) {
            if (!cfg.indicatorEl) return;
            const el = cfg.indicatorEl.jquery ? cfg.indicatorEl[0] : cfg.indicatorEl;
            if (!el) return;
            if (isError) {
                el.innerHTML = '<span style="color:#A32D2D">●</span> ' + __('Update failed — will retry');
                el.title = __('Server unreachable');
                return;
            }
            if (!lastSnapshotTime) {
                el.innerHTML = '<span style="color:#888780">○</span> ' + __('Loading…');
                return;
            }
            const ageSec = Math.floor((new Date() - lastSnapshotTime) / 1000);
            const ageLabel = ageSec < 60 ? `${ageSec}s` :
                              ageSec < 3600 ? `${Math.floor(ageSec / 60)}m` :
                              `${Math.floor(ageSec / 3600)}h`;
            const dotColor = ageSec > STALE_BADGE_AT ? '#854F0B' : '#0F6E56';
            const status = ageSec > STALE_BADGE_AT ? __('Refreshing…') : __('Live');
            el.innerHTML = `<span style="color:${dotColor}">●</span> ${status} · ` +
                           `${__('updated')} ${ageLabel} ${__('ago')}`;
            el.title = lastSnapshotTime.toLocaleString();
        }

        function bindRealtime() {
            if (realtimeBound || !frappe.realtime) return;
            try {
                frappe.realtime.on(REALTIME_EVENT, (msg) => {
                    // Only refresh if the event matches the active client,
                    // or if this dashboard wants every event (firm-wide).
                    const args = (typeof currentArgs === 'function') ? currentArgs() : {};
                    const myClient = args && args.client;
                    if (cfg.invalidateOnAnyClient || !myClient ||
                        (msg && msg.client === myClient)) {
                        fetchOnce();
                    }
                });
                realtimeBound = true;
            } catch (e) {
                console.warn('alphaxGRC.live: realtime not available', e);
            }
        }

        function bindVisibility() {
            if (!cfg.pauseWhenHidden) return;
            document.addEventListener('visibilitychange', () => {
                if (document.visibilityState === 'visible' && started) {
                    fetchOnce();
                }
            });
        }

        // Tick once a second to keep the "updated Xs ago" indicator fresh
        // even when no fetch happens.
        setInterval(updateIndicator, 1000);

        return {
            start() {
                if (started) return;
                started = true;
                bindRealtime();
                bindVisibility();
                fetchOnce();
                timer = setInterval(() => {
                    if (cfg.pauseWhenHidden && document.visibilityState !== 'visible') {
                        return;
                    }
                    fetchOnce();
                }, cfg.refreshSeconds * 1000);
            },
            stop() {
                started = false;
                if (timer) { clearInterval(timer); timer = null; }
            },
            refreshNow() {
                fetchOnce();
            },
            forceServerRefresh(client) {
                // Trigger a server-side recompute that bypasses staleness check
                frappe.call({
                    method: 'alphax_grc.dashboards_live.force_refresh',
                    args: { client: client || (currentArgs() || {}).client },
                    callback: () => fetchOnce(),
                });
            },
            setArgs(getArgsFn) {
                currentArgs = getArgsFn;
                fetchOnce();
            },
        };
    };

    // Convenience helper that returns a small jQuery node for the indicator,
    // styled to sit in a Frappe page header next to the title.
    frappe.alphaxGRC.makeIndicator = function () {
        return $(`<div class="alphax-live-indicator" style="
            display:inline-flex;align-items:center;gap:4px;
            font-size:11px;color:var(--text-muted);
            padding:3px 9px;background:rgba(0,0,0,.04);
            border-radius:999px;margin-left:8px;cursor:default">
            <span style="color:#888780">○</span> Loading…
        </div>`);
    };
})();
