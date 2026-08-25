(function () {
  "use strict";

  var API = ""; // same origin -- FastAPI serves this frontend directory itself

  function fmtMoney(v) {
    if (v === null || v === undefined || isNaN(v)) return "--";
    return "$" + Math.round(v).toLocaleString("en-US");
  }
  function fmtNum(v, d) {
    if (v === null || v === undefined || isNaN(v)) return "--";
    return Number(v).toFixed(d === undefined ? 0 : d);
  }
  function sleep(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }
  function lerp(a, b, t) { return a + (b - a) * t; }
  function lerpLatLng(a, b, t) { return [lerp(a[0], b[0], t), lerp(a[1], b[1], t)]; }
  function clamp01(t) { return t < 0 ? 0 : (t > 1 ? 1 : t); }

  async function api(path, opts) {
    var res = await fetch(API + path, opts);
    if (!res.ok) {
      var detail = "";
      try { detail = (await res.json()).detail || ""; } catch (e) {}
      throw new Error("HTTP " + res.status + (detail ? ": " + detail : ""));
    }
    return res.json();
  }

  // ======================================================================
  // TABS
  // ======================================================================
  document.querySelectorAll(".tab-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      document.querySelectorAll(".tab-btn").forEach(function (b) { b.classList.remove("active"); });
      document.querySelectorAll(".tabpanel").forEach(function (p) { p.classList.remove("active"); });
      btn.classList.add("active");
      document.getElementById("tab-" + btn.dataset.tab).classList.add("active");
      if (btn.dataset.tab === "live" && leafletMap) { setTimeout(function () { leafletMap.invalidateSize(); }, 50); }
      if (btn.dataset.tab === "compare" && !compareLoaded) loadCompare();
      if (btn.dataset.tab === "horizon" && !horizonLoaded) loadHorizon();
      if (btn.dataset.tab === "history") loadHistory();
    });
  });

  // ======================================================================
  // CONTINUOUS CITY PLAYBACK
  //
  // The engine dispatches in discrete 60-second windows (unchanged --
  // SimulationSession.WINDOW_SECONDS in engine_adapter.py). This frontend
  // maps those discrete real decisions onto ONE continuous compressed
  // simulation clock so trips from different windows can visually overlap
  // (a driver from batch N may still be mid-trip when batch N+1's requests
  // and assignments appear) instead of a "batch appears -> everything
  // drives -> everything stops -> next batch" frame-by-frame feel.
  //
  // Architecture:
  //   engineQ.queue  -- prefetched /step results, NOT yet visible
  //   playback.simTime -- the single clock driving what IS visible
  //   activateBatch() -- called only when a queued batch's window_start
  //                      has been reached by simTime (consumeDueBatches)
  //   activeTrips    -- trips currently interpolating driver_start/pickup/
  //                      dropoff; a global requestAnimationFrame loop
  //                      updates ALL of them together every frame (never
  //                      one rAF per trip, never an await-until-batch-done
  //                      barrier)
  // Engine decisions (who/fare/ETA/score) are 100% backend truth; this
  // layer only decides WHEN, visually, to reveal/interpolate them.
  // ======================================================================
  var WINDOW_SECONDS = 60;
  var BASE_SIM_SEC_PER_REAL_SEC = 60; // 1x: 1 real second = 60 simulated seconds
  var BUFFER_TARGET_BATCHES = 4;
  var HISTORY_RETENTION_SIM_SEC = 3 * WINDOW_SECONDS; // completed routes fade out after this
  var EPHEMERAL_REQUEST_RETENTION_SIM_SEC = 2 * WINDOW_SECONDS; // declined/infeasible markers

  var runGeneration = 0; // bumped on New Run / Reset; stale async producer responses are dropped
  var autoRunning = false; // Run/Pause toggles this -- gates continuous producer pumping
  var stepFetchInFlight = false; // guards manual Step against double-click while fetching

  var playback = {
    simTime: null,      // seconds -- same units as backend's window_start_seconds
    running: false,      // clock currently advancing
    speed: 1,
    buffering: false,
    stepTarget: null,   // manual Step: clock auto-pauses once simTime reaches this
    lastWallMs: null,
    loopStarted: false,
  };
  var engineQ = { done: false, producerBusy: false, queue: [] };

  var activeTrips = new Map();        // req_idx -> trip (currently interpolating)
  var activeTripByDriver = new Map(); // driver_id -> req_idx (guards reassignment conflicts)
  var historyTrail = [];              // [{trip, expireAtSim}] completed, fading out
  var ephemeralRequests = [];         // [{marker, expireAtSim}] declined/infeasible
  var driverMarkers = new Map();      // driver_id -> L.CircleMarker, persistent across batches
  var recentRows = [];                // bounded DOM rows for the operational log
  var MAX_RECENT_ROWS = 50;
  var selectedTrip = null;            // {reqIdx, batch}
  var servedEngineTotal = 0;

  // ---- driver tracking (persistent focus on searched drivers across
  // Run/Pause/Step/batch-activation -- never re-derived from the original
  // marker's own tooltip, since syncIdleDrivers() unbind/rebinds that every
  // batch). See the multi-driver tracking block below for trackedDrivers/
  // cameraTargetDriverId. ----
  var latestDriverState = new Map();  // driver_id -> last /step driver row (lat/lon/income/trips/busy)
  var lastTrackedPanMs = 0;           // throttle for camera-target auto-pan-to-keep-in-view

  // ---- map ----
  var leafletMap = null;
  // Split into granular groups so the Map Layers panel can toggle each
  // independently (pure presentation -- toggling never touches engine state).
  var mapLayers = { driver: null, activeRoute: null, historyTrail: null, requestMarkers: null, declined: null, infeasible: null, selection: null, searchFocus: null };

  function initMap() {
    if (typeof L === "undefined") {
      document.getElementById("dispatchMap").innerHTML =
        '<div class="map-fallback">Không tải được Leaflet (CDN chặn/mất mạng). ' +
        'Toàn bộ control/KPI/log vẫn hoạt động bằng dữ liệu thật, chỉ thiếu phần bản đồ.</div>';
      return;
    }
    leafletMap = L.map("dispatchMap", { zoomControl: true }).setView([40.735, -73.99], 11);
    L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
      attribution: "&copy; OpenStreetMap &copy; CARTO", subdomains: "abcd", maxZoom: 19,
    }).addTo(leafletMap);
    // layer order: history trail under active routes under request/driver markers
    mapLayers.historyTrail = L.layerGroup().addTo(leafletMap);
    mapLayers.activeRoute = L.layerGroup().addTo(leafletMap);
    mapLayers.requestMarkers = L.layerGroup().addTo(leafletMap);
    mapLayers.declined = L.layerGroup().addTo(leafletMap);
    mapLayers.infeasible = L.layerGroup().addTo(leafletMap);
    mapLayers.driver = L.layerGroup().addTo(leafletMap);
    mapLayers.selection = L.layerGroup().addTo(leafletMap);
    mapLayers.searchFocus = L.layerGroup().addTo(leafletMap);
    wireLayerToggles();
  }

  // ---- Map Layers panel: checkbox <-> Leaflet LayerGroup add/remove.
  // Pure visualization control -- never calls the API or mutates engine state. ----
  var LAYER_CHECKBOX_MAP = {
    layerDrivers: "driver", layerRequests: "requestMarkers", layerRoutes: "activeRoute",
    layerTrails: "historyTrail", layerDeclined: "declined", layerInfeasible: "infeasible",
  };
  function wireLayerToggles() {
    Object.keys(LAYER_CHECKBOX_MAP).forEach(function (checkboxId) {
      var el = document.getElementById(checkboxId);
      if (!el) return;
      el.addEventListener("change", function () {
        var lg = mapLayers[LAYER_CHECKBOX_MAP[checkboxId]];
        if (!lg || !leafletMap) return;
        if (el.checked) leafletMap.addLayer(lg); else leafletMap.removeLayer(lg);
      });
    });
  }

  function driverColorForPhase(phase) {
    if (phase === "deadhead") return "#2563EB";
    if (phase === "onboard") return "#6D28D9";
    return "#9CA3AF"; // idle
  }
  function driverStyle(phase) {
    var c = driverColorForPhase(phase);
    return { radius: phase === "idle" ? 3 : 4, color: c, weight: 1, fillOpacity: .95, fillColor: c };
  }
  function driverTooltip(driverId, phase, income, trips) {
    var label = phase === "deadhead" ? "Đang tới điểm đón" : phase === "onboard" ? "Đang chở khách" : "Đang rảnh";
    return "Tài xế #" + driverId + " -- " + label + " -- $" + fmtNum(income, 2) + " -- " + trips + " chuyến";
  }

  function getOrCreateDriverMarker(driverId, latlng, phase) {
    var m = driverMarkers.get(driverId);
    if (!m) {
      m = L.circleMarker(latlng, driverStyle(phase)).addTo(mapLayers.driver);
      driverMarkers.set(driverId, m);
    }
    return m;
  }

  // ---- driver tracking: real phase for a tracked driver, whether or not
  // it currently has an active visual trip (syncIdleDrivers only updates
  // phase for idle/non-animating drivers). ----
  function trackedDriverPhase(driverId) {
    if (activeTripByDriver.has(driverId)) {
      var reqIdx = activeTripByDriver.get(driverId);
      var trip = activeTrips.get(reqIdx);
      if (trip) return trip.phase; // "deadhead" | "onboard"
    }
    var d = latestDriverState.get(driverId);
    if (d && d.busy) return "onboard";
    return "idle";
  }

  // ---- multi-driver tracking: each tracked driver gets its own overlay
  // (focus ring + permanent tooltip) on the shared searchFocus layer, all
  // updated in place every frame -- never a new DOM node/Leaflet layer per
  // frame. Exactly one tracked driver is the camera target at a time, so
  // auto-pan never chases N drivers moving in N directions at once. ----
  var trackedDrivers = new Map(); // driverId -> { driverId, focusMarker }
  var cameraTargetDriverId = null;
  var MAX_TRACKED_DRIVERS = 10;

  function createTrackedDriverOverlay(driverId) {
    var marker = driverMarkers.get(driverId);
    var latlng = marker ? marker.getLatLng() : [0, 0];
    var ring = L.circleMarker(latlng, {
      radius: 9, weight: 2, color: "#B91C1C", fillOpacity: 0, opacity: .9, interactive: false,
      className: "driver-tracking-ring",
    }).addTo(mapLayers.searchFocus);
    ring.bindTooltip("", {
      permanent: true, direction: "top", offset: [0, -9], opacity: 1, className: "driver-tracking-tooltip",
    });
    return { driverId: driverId, focusMarker: ring };
  }

  // Repositions/re-contents ONE tracked driver's overlay; only the current
  // camera target ever triggers auto-pan (never all tracked drivers at once
  // -- that would jitter the camera if they move in different directions).
  function updateTrackedDriverOverlay(driverId, nowMs) {
    var entry = trackedDrivers.get(driverId);
    var marker = driverMarkers.get(driverId);
    if (!entry || !marker) return;
    var latlng = marker.getLatLng();
    entry.focusMarker.setLatLng(latlng);
    var isCameraTarget = driverId === cameraTargetDriverId;
    entry.focusMarker.setStyle({ weight: isCameraTarget ? 3 : 2 });
    var st = latestDriverState.get(driverId);
    entry.focusMarker.setTooltipContent(
      driverTooltip(driverId, trackedDriverPhase(driverId), st ? st.income : 0, st ? st.trips : 0)
    );
    if (isCameraTarget && leafletMap && nowMs - lastTrackedPanMs > 400) {
      var safeBounds = leafletMap.getBounds().pad(-0.15);
      if (!safeBounds.contains(latlng)) {
        leafletMap.panInside(latlng, { padding: [40, 40] });
        lastTrackedPanMs = nowMs;
      }
    }
  }

  function updateAllTrackedDriversFocus(nowMs) {
    trackedDrivers.forEach(function (entry, driverId) { updateTrackedDriverOverlay(driverId, nowMs); });
  }

  function renderTrackingPanel() {
    var panel = document.getElementById("trackingPanel");
    if (!panel) return;
    var chipsEl = document.getElementById("trackingChips");
    if (trackedDrivers.size === 0) { panel.style.display = "none"; chipsEl.innerHTML = ""; return; }
    panel.style.display = "block";
    document.getElementById("trackingPanelLabel").textContent = "Đang theo dõi " + trackedDrivers.size + " tài xế";
    chipsEl.innerHTML = "";
    trackedDrivers.forEach(function (entry, driverId) {
      var chip = document.createElement("span");
      chip.className = "tracking-chip" + (driverId === cameraTargetDriverId ? " active" : "");
      var body = document.createElement("span");
      body.className = "tracking-chip-body";
      body.textContent = "Tài xế #" + driverId;
      body.title = "Focus camera vào Tài xế #" + driverId;
      body.addEventListener("click", function () { setCameraTarget(driverId); });
      var removeBtn = document.createElement("button");
      removeBtn.className = "chip-remove";
      removeBtn.textContent = "×";
      removeBtn.setAttribute("aria-label", "Ngừng theo dõi Tài xế #" + driverId);
      removeBtn.title = "Ngừng theo dõi Tài xế #" + driverId;
      removeBtn.addEventListener("click", function (e) { e.stopPropagation(); removeTrackedDriver(driverId); });
      chip.appendChild(body);
      chip.appendChild(removeBtn);
      chipsEl.appendChild(chip);
    });
  }

  function setCameraTarget(driverId) {
    if (!trackedDrivers.has(driverId)) return;
    cameraTargetDriverId = driverId;
    var marker = driverMarkers.get(driverId);
    if (leafletMap && marker) leafletMap.panTo(marker.getLatLng());
    lastTrackedPanMs = performance.now();
    renderTrackingPanel();
  }

  // Search = add to tracking (never replaces existing tracked drivers).
  // Re-searching an already-tracked driver just re-focuses the camera --
  // no duplicate overlay.
  function addOrFocusTrackedDriver(id) {
    if (trackedDrivers.has(id)) {
      setCameraTarget(id);
      return { ok: true, alreadyTracked: true };
    }
    if (trackedDrivers.size >= MAX_TRACKED_DRIVERS) return { ok: false, alreadyTracked: false };
    trackedDrivers.set(id, createTrackedDriverOverlay(id));
    updateTrackedDriverOverlay(id, performance.now());
    setCameraTarget(id);
    return { ok: true, alreadyTracked: false };
  }

  function removeTrackedDriver(driverId) {
    var entry = trackedDrivers.get(driverId);
    if (!entry) return;
    mapLayers.searchFocus.removeLayer(entry.focusMarker);
    trackedDrivers.delete(driverId);
    if (cameraTargetDriverId === driverId) {
      var fallback = null;
      trackedDrivers.forEach(function (e, id) { fallback = id; }); // most-recently-added remaining driver
      cameraTargetDriverId = fallback;
    }
    renderTrackingPanel();
  }

  function clearAllTrackedDrivers() {
    trackedDrivers.forEach(function (entry) { mapLayers.searchFocus.removeLayer(entry.focusMarker); });
    trackedDrivers.clear();
    cameraTargetDriverId = null;
    renderTrackingPanel();
  }

  // Drivers WITHOUT an active visual trip get synced straight from backend
  // state (idle drivers don't move). Drivers WITH an active trip are owned
  // by the global clock -- backend's post-commit r.drivers state must NEVER
  // snap/teleport their marker mid-animation (see section 22-24 of the
  // continuous-playback spec).
  function syncIdleDrivers(r) {
    if (!leafletMap) return;
    r.drivers.forEach(function (d) {
      latestDriverState.set(d.driver_id, d); // cache for tracking BEFORE the active-trip skip below
      if (activeTripByDriver.has(d.driver_id)) return; // clock owns this marker right now
      var m = driverMarkers.get(d.driver_id);
      var phase = d.busy ? "onboard" : "idle"; // best-effort label for non-animating drivers
      if (!m) {
        m = L.circleMarker([d.lat, d.lon], driverStyle(phase)).addTo(mapLayers.driver);
        driverMarkers.set(d.driver_id, m);
      } else {
        m.setLatLng([d.lat, d.lon]);
        m.setStyle(driverStyle(phase));
      }
      m.unbindTooltip();
      m.bindTooltip(driverTooltip(d.driver_id, phase, d.income, d.trips));
    });
  }

  function removeTripLayers(trip) {
    [trip.deadheadLine, trip.tripLine].forEach(function (layer) {
      if (layer) { mapLayers.activeRoute.removeLayer(layer); mapLayers.historyTrail.removeLayer(layer); }
    });
    [trip.pickupMarker, trip.dropoffMarker].forEach(function (marker) {
      if (marker) mapLayers.requestMarkers.removeLayer(marker);
    });
  }

  // ---- recent operations log: bounded, append-only, rows update in place
  // as a trip's phase changes (never wiped wholesale per batch) ----
  function appendRecentRow(trip) {
    var tbody = document.querySelector("#assignTable tbody");
    var tr = document.createElement("tr");
    tr.className = "clickable";
    tr.dataset.reqIdx = trip.reqIdx;
    tr.dataset.batch = trip.batch;
    tr.innerHTML = "<td>#" + trip.batch + "</td><td>#" + trip.reqIdx + "</td><td>Tài xế #" + trip.driverId +
      "</td><td class='num'>" + fmtMoney(trip.fare) + "</td><td>" + trip.pickupZone + "</td><td>" + trip.dropoffZone +
      "</td><td class='phase-cell'>ĐANG TỚI ĐÓN</td>";
    tr.addEventListener("click", function () { toggleAssignmentSelection(trip.reqIdx, trip.batch); });
    tbody.insertBefore(tr, tbody.firstChild); // newest first
    recentRows.unshift({ reqIdx: trip.reqIdx, tr: tr });
    while (recentRows.length > MAX_RECENT_ROWS) {
      var old = recentRows.pop();
      if (old.tr.parentNode) old.tr.parentNode.removeChild(old.tr);
    }
    return tr;
  }
  function updateRowPhase(trip) {
    if (!trip.rowEl) return;
    var cell = trip.rowEl.querySelector(".phase-cell");
    if (!cell) return;
    cell.textContent = trip.phase === "deadhead" ? "ĐANG TỚI ĐÓN" : trip.phase === "onboard" ? "ĐANG CHỞ KHÁCH" : "HOÀN TẤT";
  }
  function clearAssignTableRows() {
    document.querySelector("#assignTable tbody").innerHTML = "";
    recentRows = [];
  }

  // ---- batch activation: reveal a prefetched /step result on the map ----
  function activateBatch(batch) {
    renderKpi(batch.metrics);
    renderHistogram(batch.income_histogram);
    renderLorenz(batch.lorenz);
    updateStatusGrid(batch);
    servedEngineTotal = batch.metrics.served_total;
    var svc = updateServiceHealth(batch);
    var fair = updateFairnessSummary(batch);
    evaluateAlerts(svc, fair);
    if (typeof lastBatchMetrics !== "undefined") {
      lastBatchMetrics = { utility: batch.metrics.utility, gini: batch.metrics.gini, served_total: batch.metrics.served_total, batch: batch.batch };
    }
    syncIdleDrivers(batch);

    (batch.declined_requests || []).forEach(function (req) {
      var m = L.circleMarker([req.pickup_lat, req.pickup_lon], { radius: 4, color: "#D97706", weight: 2, fillColor: "#D97706", fillOpacity: .6 })
        .bindTooltip("Bị từ chối -- yêu cầu #" + req.req_idx + " -- khu " + req.pickup_zone)
        .addTo(mapLayers.declined);
      ephemeralRequests.push({ marker: m, layer: mapLayers.declined, expireAtSim: playback.simTime + EPHEMERAL_REQUEST_RETENTION_SIM_SEC });
    });
    (batch.infeasible_requests || []).forEach(function (req) {
      var m = L.circleMarker([req.pickup_lat, req.pickup_lon], { radius: 4, color: "#6B7280", weight: 1.4, fillOpacity: 0 })
        .bindTooltip("Không khả thi -- yêu cầu #" + req.req_idx + " -- không có tài xế trong bán kính 600s -- khu " + req.pickup_zone)
        .addTo(mapLayers.infeasible);
      ephemeralRequests.push({ marker: m, layer: mapLayers.infeasible, expireAtSim: playback.simTime + EPHEMERAL_REQUEST_RETENTION_SIM_SEC });
    });

    batch.assignments.forEach(function (a) {
      if (activeTripByDriver.has(a.driver_id)) {
        // Should not happen -- simulator only offers a driver when
        // available_at <= window_start -- but guard defensively rather than
        // silently overwrite a still-moving visual trip.
        console.warn("visual/engine conflict: driver", a.driver_id, "reassigned while a visual trip was still active");
        var prevReqIdx = activeTripByDriver.get(a.driver_id);
        var prevTrip = activeTrips.get(prevReqIdx);
        if (prevTrip) { completeVisualTrip(prevTrip); activeTrips.delete(prevReqIdx); }
      }
      var startSim = batch.window_start_seconds;
      var pickupSim = startSim + (a.pickup_eta_seconds || 0);
      var dropoffSim = pickupSim + (a.duration_seconds || 0);
      var startLatLng = [a.driver_start_lat, a.driver_start_lon];
      var pickupLatLng = [a.pickup_lat, a.pickup_lon];
      var dropoffLatLng = [a.dropoff_lat, a.dropoff_lon];

      var trip = {
        reqIdx: a.req_idx, driverId: a.driver_id, batch: batch.batch,
        startSim: startSim, pickupSim: pickupSim, dropoffSim: dropoffSim,
        startLatLng: startLatLng, pickupLatLng: pickupLatLng, dropoffLatLng: dropoffLatLng,
        bounds: [startLatLng, pickupLatLng, dropoffLatLng],
        fare: a.fare, pickupZone: a.pickup_zone, dropoffZone: a.dropoff_zone,
        phase: "deadhead",
      };
      trip.marker = getOrCreateDriverMarker(a.driver_id, startLatLng, "deadhead");
      trip.marker.setLatLng(startLatLng);
      trip.marker.setStyle(driverStyle("deadhead"));
      trip.deadheadLine = L.polyline([startLatLng, pickupLatLng], { color: "#9CA3AF", weight: 1.6, dashArray: "4,4", opacity: .85 }).addTo(mapLayers.activeRoute);
      trip.tripLine = L.polyline([pickupLatLng, dropoffLatLng], { color: "#17365D", weight: 2, opacity: .3 }).addTo(mapLayers.activeRoute);
      trip.pickupMarker = L.circleMarker(pickupLatLng, { radius: 4.5, color: "#fff", weight: 1.5, fillColor: "#15803D", fillOpacity: 1 })
        .bindTooltip("Đón khách -- yêu cầu #" + a.req_idx + " -- khu " + a.pickup_zone + " -- $" + fmtNum(a.fare, 2))
        .addTo(mapLayers.requestMarkers);
      trip.dropoffMarker = L.circleMarker(dropoffLatLng, { radius: 4.5, color: "#fff", weight: 1.5, fillColor: "#B45309", fillOpacity: 1 })
        .bindTooltip("Trả khách -- yêu cầu #" + a.req_idx + " -- khu " + a.dropoff_zone)
        .addTo(mapLayers.requestMarkers);
      [trip.deadheadLine, trip.tripLine, trip.pickupMarker, trip.dropoffMarker].forEach(function (layer) {
        layer.on("click", function () { toggleAssignmentSelection(trip.reqIdx, trip.batch); });
      });
      trip.rowEl = appendRecentRow(trip);

      activeTrips.set(a.req_idx, trip);
      activeTripByDriver.set(a.driver_id, a.req_idx);
    });
    updateAllTrackedDriversFocus(performance.now()); // avoid a stale frame right as this batch reveals
  }

  function completeVisualTrip(trip) {
    trip.phase = "done";
    updateRowPhase(trip);
    activeTripByDriver.delete(trip.driverId);
    if (trip.deadheadLine) trip.deadheadLine.setStyle({ opacity: .18 });
    if (trip.tripLine) { mapLayers.activeRoute.removeLayer(trip.tripLine); trip.tripLine.setStyle({ opacity: .18 }); mapLayers.historyTrail.addLayer(trip.tripLine); }
    if (trip.deadheadLine) { mapLayers.activeRoute.removeLayer(trip.deadheadLine); mapLayers.historyTrail.addLayer(trip.deadheadLine); }
    historyTrail.push({ trip: trip, expireAtSim: playback.simTime + HISTORY_RETENTION_SIM_SEC });
  }

  function purgeExpired(simTime) {
    historyTrail = historyTrail.filter(function (item) {
      if (simTime >= item.expireAtSim) {
        removeTripLayers(item.trip);
        if (item.trip.rowEl && item.trip.rowEl.parentNode) { /* keep row in log, just visually done */ }
        if (selectedTrip && selectedTrip.reqIdx === item.trip.reqIdx && selectedTrip.batch === item.trip.batch) {
          clearAssignmentSelection(); // spec 40: auto-clear only once retention has elapsed
        }
        return false;
      }
      return true;
    });
    ephemeralRequests = ephemeralRequests.filter(function (item) {
      if (simTime >= item.expireAtSim) { item.layer.removeLayer(item.marker); return false; }
      return true;
    });
  }

  // ---- per-frame trip interpolation (pure presentation of already-real
  // driver_start/pickup/dropoff coordinates -- see header comment) ----
  function updateActiveTrips(simTime) {
    if (simTime === null) return;
    activeTrips.forEach(function (trip, key) {
      if (simTime < trip.pickupSim) {
        var p = trip.pickupSim > trip.startSim ? clamp01((simTime - trip.startSim) / (trip.pickupSim - trip.startSim)) : 1;
        trip.marker.setLatLng(lerpLatLng(trip.startLatLng, trip.pickupLatLng, p));
        if (trip.phase !== "deadhead") { trip.phase = "deadhead"; trip.marker.setStyle(driverStyle("deadhead")); updateRowPhase(trip); }
      } else if (simTime < trip.dropoffSim) {
        if (trip.phase !== "onboard") {
          trip.phase = "onboard";
          trip.marker.setStyle(driverStyle("onboard"));
          trip.deadheadLine.setStyle({ opacity: .25 });
          trip.tripLine.setStyle({ opacity: .8 });
          updateRowPhase(trip);
        }
        var p2 = trip.dropoffSim > trip.pickupSim ? clamp01((simTime - trip.pickupSim) / (trip.dropoffSim - trip.pickupSim)) : 1;
        trip.marker.setLatLng(lerpLatLng(trip.pickupLatLng, trip.dropoffLatLng, p2));
      } else {
        trip.marker.setLatLng(trip.dropoffLatLng);
        completeVisualTrip(trip);
        activeTrips.delete(key);
      }
    });
  }

  // ---- assignment selection: toggle open/close, works across batches ----
  function clearAssignmentSelection() {
    selectedTrip = null;
    document.querySelectorAll("#assignTable tbody tr").forEach(function (tr) { tr.classList.remove("selected"); });
    if (mapLayers.selection) mapLayers.selection.clearLayers();
    document.getElementById("trackerEmpty").style.display = "block";
    document.getElementById("trackerBody").style.display = "none";
    document.getElementById("trackerClose").style.display = "none";
  }

  async function toggleAssignmentSelection(reqIdx, batch) {
    if (selectedTrip && selectedTrip.reqIdx === reqIdx && selectedTrip.batch === batch) { clearAssignmentSelection(); return; }
    // Driver tracking and Request selection are independent -- searching a
    // Request no longer clears tracked drivers (see multi-driver tracking).
    selectedTrip = { reqIdx: reqIdx, batch: batch };
    document.querySelectorAll("#assignTable tbody tr").forEach(function (tr) {
      tr.classList.toggle("selected", parseInt(tr.dataset.reqIdx, 10) === reqIdx && parseInt(tr.dataset.batch, 10) === batch);
    });
    highlightSelection(reqIdx);
    document.getElementById("trackerClose").style.display = "inline-block";
    await explainAssignment(reqIdx, batch);
  }

  document.getElementById("trackerClose").addEventListener("click", clearAssignmentSelection);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && selectedTrip !== null) clearAssignmentSelection();
  });

  function findTrip(reqIdx) {
    if (activeTrips.has(reqIdx)) return activeTrips.get(reqIdx);
    for (var i = 0; i < historyTrail.length; i++) { if (historyTrail[i].trip.reqIdx === reqIdx) return historyTrail[i].trip; }
    return null;
  }

  function highlightSelection(reqIdx) {
    mapLayers.selection.clearLayers();
    var trip = findTrip(reqIdx);
    if (!trip) return;
    L.polyline([trip.startLatLng, trip.pickupLatLng], { color: "#17365D", weight: 3, dashArray: "4,4", opacity: .95 }).addTo(mapLayers.selection);
    L.polyline([trip.pickupLatLng, trip.dropoffLatLng], { color: "#15803D", weight: 4, opacity: .95 }).addTo(mapLayers.selection);
    // no auto-fit-bounds while playback is running (avoid jarring camera jumps) --
    // only fit if the map isn't actively animating other trips right now.
  }

  // ---- speed control ----
  document.querySelectorAll(".speed-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      playback.speed = parseFloat(btn.dataset.speed);
      document.querySelectorAll(".speed-btn").forEach(function (b) { b.classList.remove("active"); });
      btn.classList.add("active");
    });
  });

  // ======================================================================
  // GLOBAL CLOCK LOOP -- the single requestAnimationFrame driving every
  // active trip, buffering detection, and batch activation. There is no
  // per-trip rAF and no "await Promise.all(batch) before next fetch"
  // barrier anywhere in this file.
  // ======================================================================
  function consumeDueBatches() {
    if (playback.simTime === null) return;
    while (engineQ.queue.length && engineQ.queue[0].window_start_seconds <= playback.simTime) {
      activateBatch(engineQ.queue.shift());
      if (autoRunning) pumpEngine(runGeneration);
    }
  }

  function playbackLoop(nowMs) {
    requestAnimationFrame(playbackLoop);
    if (playback.lastWallMs == null) playback.lastWallMs = nowMs;
    var dtWall = (nowMs - playback.lastWallMs) / 1000;
    playback.lastWallMs = nowMs;
    if (dtWall > 0.25) dtWall = 0.25; // clamp huge gaps (tab backgrounded, devtools pause, etc.)

    if (playback.running && playback.simTime !== null) {
      var waitingOnEngine = autoRunning && engineQ.queue.length === 0 && !engineQ.done && playback.stepTarget === null;
      playback.buffering = waitingOnEngine;
      if (!waitingOnEngine) {
        var advance = dtWall * BASE_SIM_SEC_PER_REAL_SEC * playback.speed;
        var newTime = playback.simTime + advance;
        if (playback.stepTarget !== null && newTime >= playback.stepTarget) {
          newTime = playback.stepTarget;
          playback.running = false;
          playback.stepTarget = null;
        }
        playback.simTime = newTime;
      }
    } else {
      playback.buffering = false;
    }

    consumeDueBatches();
    updateActiveTrips(playback.simTime);
    updateAllTrackedDriversFocus(nowMs);
    purgeExpired(playback.simTime === null ? -Infinity : playback.simTime);
    updatePlaybackUI();
  }

  function ensureLoopStarted() {
    if (playback.loopStarted) return;
    playback.loopStarted = true;
    playback.lastWallMs = null;
    requestAnimationFrame(playbackLoop);
  }

  function p2(n) { return (n < 10 ? "0" : "") + n; }

  // Real calendar date/time from the dataset itself (t0EpochSeconds = the
  // actual NYC TLC timestamp that window_start_seconds=0 corresponds to),
  // not a synthetic "Day 1" counter -- easier to place a batch in context.
  // Uses UTC getters deliberately: the parquet timestamp carries no
  // timezone, so UTC formatting shows exactly the wall-clock value stored
  // in the data without the browser's local timezone silently shifting it.
  function formatSimTime(sec) {
    if (sec === null || sec === undefined) return "--";
    var relS = Math.floor(sec % 86400);
    var day = Math.floor(sec / 86400) + 1;
    var hh = Math.floor(relS / 3600), mm = Math.floor((relS % 3600) / 60), ss = Math.floor(relS % 60);
    var relLabel = "Ngày " + day + " · " + p2(hh) + ":" + p2(mm) + ":" + p2(ss);
    if (t0EpochSeconds === null || t0EpochSeconds === undefined) return relLabel;
    var d = new Date((t0EpochSeconds + sec) * 1000);
    var dateLabel = p2(d.getUTCDate()) + "/" + p2(d.getUTCMonth() + 1) + "/" + d.getUTCFullYear() +
      " " + p2(d.getUTCHours()) + ":" + p2(d.getUTCMinutes()) + ":" + p2(d.getUTCSeconds());
    return dateLabel + " (" + relLabel + ")";
  }

  function updatePlaybackUI() {
    document.getElementById("bufferingBadge").style.display = playback.buffering ? "inline-block" : "none";
    var sg = document.getElementById("statusGrid");
    if (sg.style.display === "none") return;
    document.getElementById("sgSimTime").textContent = formatSimTime(playback.simTime);
    document.getElementById("sgActiveTrips").textContent = activeTrips.size;
    document.getElementById("sgQueued").textContent = engineQ.queue.length;
    document.getElementById("sgServed").textContent = servedEngineTotal;
  }

  function updateStatusGrid(batch) {
    var sg = document.getElementById("statusGrid");
    sg.style.display = "grid";
    document.getElementById("sgProgress").textContent = batch.metrics.requests_consumed + " / " + batch.metrics.requests_total;
    elBatchLine.innerHTML = "Batch <b>#" + batch.batch + "</b> activated · " + formatSimTime(batch.window_start_seconds) +
      (batch.done ? " · <b>đã hết dữ liệu để lấy thêm</b>" : "");
  }

  // ---- engine producer: sequential /step calls filling a small buffer,
  // never concurrent (session lock on the backend is unchanged) ----
  async function pumpEngine(gen) {
    if (engineQ.producerBusy) return;
    engineQ.producerBusy = true;
    try {
      while (autoRunning && !engineQ.done && engineQ.queue.length < BUFFER_TARGET_BATCHES && gen === runGeneration) {
        var r;
        try {
          r = await api("/simulations/" + currentRunId + "/step", { method: "POST" });
        } catch (e) {
          if (String(e.message).indexOf("409") !== -1) { await sleep(50); continue; }
          elBatchLine.textContent = "Lỗi engine: " + e.message;
          break;
        }
        if (gen !== runGeneration) return; // stale -- New Run/Reset happened meanwhile
        if (r.done && r.assignments === undefined) { engineQ.done = true; break; }
        engineQ.queue.push(r);
        if (playback.simTime === null) playback.simTime = r.window_start_seconds; // spec 79: start clock at first batch
        if (r.done) { engineQ.done = true; break; }
      }
    } finally {
      engineQ.producerBusy = false;
    }
  }

  async function ensureOneQueuedBatch() {
    if (engineQ.queue.length > 0 || engineQ.done) return;
    var gen = runGeneration;
    var r;
    try {
      r = await api("/simulations/" + currentRunId + "/step", { method: "POST" });
    } catch (e) {
      if (String(e.message).indexOf("409") === -1) elBatchLine.textContent = "Lỗi engine: " + e.message;
      return;
    }
    if (gen !== runGeneration) return;
    if (r.done && r.assignments === undefined) { engineQ.done = true; return; }
    engineQ.queue.push(r);
    if (playback.simTime === null) playback.simTime = r.window_start_seconds;
    if (r.done) engineQ.done = true;
  }

  // ======================================================================
  // LIVE SIMULATION controls
  // ======================================================================
  var currentRunId = null;
  var t0EpochSeconds = null; // real Unix epoch seconds for window_start_seconds=0 in this run's dataset

  var elStep = document.getElementById("btnStep");
  var elRun = document.getElementById("btnRun");
  var elPause = document.getElementById("btnPause");
  var elReset = document.getElementById("btnReset");
  var elNewRun = document.getElementById("btnNewRun");
  var elRunIdLabel = document.getElementById("runIdLabel");
  var elBatchLine = document.getElementById("batchLine");
  var elProgressHint = document.getElementById("progressHint");
  var elPolicySelect = document.getElementById("cfgPolicy");
  var elFieldLam = document.getElementById("fieldLam");
  var elFieldForecast = document.getElementById("fieldForecast");
  var elMomaqlNote = document.getElementById("momaqlOnlyNote");

  document.getElementById("cfgLam").addEventListener("input", function (e) {
    document.getElementById("cfgLamVal").textContent = e.target.value;
    // user dragging the slider by hand = a value not covered by the 3
    // presets -- reflect that as Custom rather than leaving a stale preset
    // highlighted (Objective label must always match the λ actually sent).
    document.querySelectorAll(".obj-btn[data-lambda]").forEach(function (b) { b.classList.remove("active"); });
    var customBtn = document.querySelector('.obj-btn[data-lambda="custom"]');
    if (customBtn) customBtn.classList.add("active");
    updateScenarioSummary();
  });

  // ---- P1.6 (kept): context-aware controls -- lambda/forecast only mean
  // anything for MOMAQL. ----
  function updateContextAwareControls() {
    var isMomaql = elPolicySelect.value === "MOMAQL";
    elFieldLam.classList.toggle("disabled", !isMomaql);
    elFieldForecast.classList.toggle("disabled", !isMomaql);
    document.getElementById("cfgLam").disabled = !isMomaql;
    document.getElementById("cfgForecast").disabled = !isMomaql;
    elMomaqlNote.style.display = isMomaql ? "none" : "block";
    document.getElementById("fieldObjective").classList.toggle("disabled", !isMomaql);
    document.querySelectorAll(".obj-btn[data-lambda]").forEach(function (b) { b.disabled = !isMomaql; });
    updateScenarioSummary();
  }
  elPolicySelect.addEventListener("change", updateContextAwareControls);
  updateContextAwareControls();
  document.getElementById("cfgForecast").addEventListener("change", function () { updateScenarioSummary(); });

  // ---- Operating Objective: Efficiency/Balanced/Fairness map to real MOMAQL
  // λ (0.1/0.5/0.9 -- operator-facing labels, not a paper-defined mapping,
  // per audit requirement). Custom reveals the raw λ slider. ----
  document.querySelectorAll(".obj-btn[data-lambda]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      if (btn.disabled) return;
      document.querySelectorAll(".obj-btn[data-lambda]").forEach(function (b) { b.classList.remove("active"); });
      btn.classList.add("active");
      var v = btn.dataset.lambda;
      var fieldLamEl = document.getElementById("fieldLam");
      if (v === "custom") {
        fieldLamEl.style.display = "block";
      } else {
        fieldLamEl.style.display = "none";
        document.getElementById("cfgLam").value = v;
        document.getElementById("cfgLamVal").textContent = v;
      }
    });
  });
  function currentObjectiveLabel() {
    if (elPolicySelect.value !== "MOMAQL") return "Do chiến lược quyết định";
    var active = document.querySelector(".obj-btn[data-lambda].active");
    return active ? active.textContent : "Tùy chỉnh";
  }

  // ---- Simulation Horizon presets: user-facing language for request_limit
  // (raw count only in Advanced/Custom), mapped to real values. Quick=200 /
  // Standard=3000 (current product default) / Extended=10000, per audit of
  // FairDispatch_Operator_Control_Presets_TimeFilters_Requirements.md §Phase 4. ----
  document.querySelectorAll(".obj-btn[data-limit]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      document.querySelectorAll(".obj-btn[data-limit]").forEach(function (b) { b.classList.remove("active"); });
      btn.classList.add("active");
      var v = btn.dataset.limit;
      var customField = document.getElementById("fieldLimitCustom");
      var warning = document.getElementById("horizonWarning");
      if (v === "custom") {
        customField.style.display = "block";
        warning.style.display = parseInt(document.getElementById("cfgLimit").value, 10) >= 10000 ? "block" : "none";
      } else {
        customField.style.display = "none";
        document.getElementById("cfgLimit").value = v;
        warning.style.display = (parseInt(v, 10) >= 10000) ? "block" : "none";
      }
      updateScenarioSummary();
    });
  });
  document.getElementById("cfgLimit").addEventListener("input", function () {
    document.getElementById("horizonWarning").style.display = (parseInt(this.value, 10) || 0) >= 10000 ? "block" : "none";
    updateScenarioSummary();
  });

  // ---- Fleet presets: 100/200/400 (canonical research sweep values) /
  // Custom -- this control changes the REAL engine fleet size (n_drivers
  // in POST /simulations), never a visual "how many cars to animate" limit. ----
  document.querySelectorAll(".obj-btn[data-fleet]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      document.querySelectorAll(".obj-btn[data-fleet]").forEach(function (b) { b.classList.remove("active"); });
      btn.classList.add("active");
      var v = btn.dataset.fleet;
      var customField = document.getElementById("fieldDriversCustom");
      if (v === "custom") {
        customField.style.display = "block";
      } else {
        customField.style.display = "none";
        document.getElementById("cfgDrivers").value = v;
      }
      updateScenarioSummary();
    });
  });
  document.getElementById("cfgDrivers").addEventListener("input", updateScenarioSummary);

  // ---- Time-of-day scenario filter: filters which real dataset requests
  // the engine receives (backend engine_adapter.apply_scenario_filters),
  // never a visual/post-hoc filter -- see PHASE 21 of the scenario-controls spec. ----
  var TIME_PRESETS = {
    all: null,
    morning_peak: { start: 6, end: 9 },
    evening_peak: { start: 17, end: 19 },
    night: { start: 22, end: 5 },
  };
  document.querySelectorAll(".obj-btn[data-time]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      document.querySelectorAll(".obj-btn[data-time]").forEach(function (b) { b.classList.remove("active"); });
      btn.classList.add("active");
      var mode = btn.dataset.time;
      document.getElementById("fieldTimeCustom").style.display = (mode === "custom") ? "block" : "none";
      var preset = TIME_PRESETS[mode];
      if (preset) {
        document.getElementById("timeStartHour").value = preset.start;
        document.getElementById("timeEndHour").value = preset.end;
      }
      updateScenarioSummary();
    });
  });
  document.getElementById("timeStartHour").addEventListener("input", updateScenarioSummary);
  document.getElementById("timeEndHour").addEventListener("input", updateScenarioSummary);

  document.querySelectorAll(".obj-btn[data-day]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      document.querySelectorAll(".obj-btn[data-day]").forEach(function (b) { b.classList.remove("active"); });
      btn.classList.add("active");
      document.getElementById("fieldDayCustom").style.display = (btn.dataset.day === "custom") ? "block" : "none";
      updateScenarioSummary();
    });
  });
  document.querySelectorAll(".day-cb").forEach(function (cb) { cb.addEventListener("change", updateScenarioSummary); });

  var DAY_NAMES = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"];

  function getTimeFilterMode() {
    var active = document.querySelector(".obj-btn[data-time].active");
    return active ? active.dataset.time : "all";
  }
  function getTimeFilterPayload() {
    var mode = getTimeFilterMode();
    if (mode === "all") return { mode: "all" };
    var start = parseInt(document.getElementById("timeStartHour").value, 10);
    var end = parseInt(document.getElementById("timeEndHour").value, 10);
    return { mode: mode, start_hour: isNaN(start) ? 0 : start, end_hour: isNaN(end) ? 0 : end };
  }
  function getDayFilterMode() {
    var active = document.querySelector(".obj-btn[data-day].active");
    return active ? active.dataset.day : "all";
  }
  function getDayFilterPayload() {
    var mode = getDayFilterMode();
    if (mode === "custom") {
      var days = Array.prototype.slice.call(document.querySelectorAll(".day-cb:checked")).map(function (cb) { return parseInt(cb.value, 10); });
      return { mode: "custom", days: days };
    }
    return { mode: mode };
  }

  // ---- Scenario summary + "SCENARIO FILTER ACTIVE" badge: computed from
  // the current form state, before New Run is even clicked, so the operator
  // sees exactly what they are about to run. ----
  function updateScenarioSummary() {
    var timeMode = getTimeFilterMode(), dayMode = getDayFilterMode();
    var timeLabel = timeMode === "all" ? "Cả ngày"
      : timeMode === "custom" ? (document.getElementById("timeStartHour").value + "h–" + document.getElementById("timeEndHour").value + "h")
      : document.querySelector(".obj-btn[data-time].active").textContent + " (" +
        TIME_PRESETS[timeMode].start + "h–" + TIME_PRESETS[timeMode].end + "h)";
    var dayLabel = dayMode === "all" ? "Cả tuần"
      : dayMode === "weekday" ? "Ngày thường"
      : dayMode === "weekend" ? "Cuối tuần"
      : (function () {
          var days = Array.prototype.slice.call(document.querySelectorAll(".day-cb:checked")).map(function (cb) { return DAY_NAMES[parseInt(cb.value, 10)]; });
          return days.length ? days.join("/") : "(chưa chọn ngày)";
        })();
    var horizonBtn = document.querySelector(".obj-btn[data-limit].active");
    var horizonLabel = (horizonBtn ? horizonBtn.textContent : "Tùy chỉnh") + " · " +
      (parseInt(document.getElementById("cfgLimit").value, 10) || 0).toLocaleString("en-US") + " request";
    var fleetVal = document.getElementById("cfgDrivers").value;

    document.getElementById("scenarioSummary").innerHTML =
      "<b>" + currentObjectiveLabel() + "</b> &middot; " + elPolicySelect.value + " &middot; " + fleetVal + " driver &middot; " +
      "Forecast " + (document.getElementById("cfgForecast").checked ? "ON" : "OFF") + "<br>" +
      timeLabel + " &middot; " + dayLabel + "<br>" +
      "Validation &middot; " + horizonLabel;

    var isActive = timeMode !== "all" || dayMode !== "all";
    var badge = document.getElementById("scenarioActiveBadge");
    if (isActive) {
      badge.style.display = "inline-block";
      badge.textContent = "BỘ LỌC KỊCH BẢN ĐANG BẬT · " + dayLabel + " · " + timeLabel;
    } else {
      badge.style.display = "none";
    }
  }
  updateScenarioSummary();

  // ---- Save Run: snapshots the CURRENT run's real scenario config + latest
  // real metrics to localStorage (client-only -- no backend endpoint needed,
  // per spec's explicit "localStorage or JSON export is enough"). ----
  var lastBatchMetrics = null;
  var lastRunConfig = null;
  document.getElementById("btnSaveRun").addEventListener("click", function () {
    if (!currentRunId || !lastRunConfig) return;
    var saved = JSON.parse(localStorage.getItem("fd_saved_runs") || "[]");
    saved.unshift({
      saved_at: new Date().toISOString(), run_id: currentRunId, config: lastRunConfig,
      metrics: lastBatchMetrics,
    });
    if (saved.length > 20) saved.length = 20;
    localStorage.setItem("fd_saved_runs", JSON.stringify(saved));
    document.getElementById("saveRunResult").innerHTML = "Run <b>" + currentRunId + "</b> đã lưu (localStorage, " + saved.length + " run đã lưu).";
  });

  // ---- Search: Driver ID / Request ID against what's actually retained in
  // the current playback buffer -- never fakes a result. ----
  function doSearch() {
    var raw = document.getElementById("searchInput").value.trim();
    var resultEl = document.getElementById("searchResult");
    if (!raw) { resultEl.textContent = ""; return; }
    var id = parseInt(raw, 10);
    if (isNaN(id)) { resultEl.textContent = "Nhập ID số (Driver ID hoặc Request ID)."; return; }
    if (driverMarkers.has(id)) {
      var res = addOrFocusTrackedDriver(id);
      if (!res.ok) {
        resultEl.innerHTML = "Bạn có thể theo dõi tối đa " + MAX_TRACKED_DRIVERS + " tài xế cùng lúc.<br>" +
          "Hãy bỏ theo dõi một tài xế trước khi thêm tài xế mới.";
      } else if (res.alreadyTracked) {
        resultEl.innerHTML = "Tài xế #" + id + " đang được theo dõi.";
      } else {
        resultEl.innerHTML = "Đang theo dõi <b>Tài xế #" + id + "</b>. Vị trí và trạng thái sẽ được cập nhật khi mô phỏng chạy.";
      }
      return;
    }
    var trip = findTrip(id);
    if (trip) {
      toggleAssignmentSelection(trip.reqIdx, trip.batch);
      resultEl.innerHTML = "Tìm thấy <b>Yêu cầu #" + id + "</b> (đợt #" + trip.batch + ") &mdash; đã mở Vì sao chọn tài xế này.";
      return;
    }
    resultEl.textContent = "Không có trong bộ đệm phát lại hiện tại -- Tài xế #" + id + " / Yêu cầu #" + id + " không có trong dữ liệu đang hiển thị.";
  }
  document.getElementById("searchBtn").addEventListener("click", doSearch);
  document.getElementById("searchInput").addEventListener("keydown", function (e) { if (e.key === "Enter") doSearch(); });
  document.getElementById("btnUntrackAll").addEventListener("click", function () {
    clearAllTrackedDrivers();
    document.getElementById("searchResult").textContent = "";
  });

  // ---- Service Health / Fairness Guardrail / Alert Center -- operator-
  // defined demo thresholds, explicitly NOT claimed as paper findings. ----
  var MIN_SERVICE_RATE = 0.90;
  var MAX_PICKUP_P90_SEC = 8 * 60;
  var SHORTAGE_RATIO_THRESHOLD = 1.5;

  (function loadGuardrail() {
    var saved = localStorage.getItem("fd_max_gini");
    if (saved) document.getElementById("maxGiniInput").value = saved;
  })();
  document.getElementById("maxGiniInput").addEventListener("change", function () {
    localStorage.setItem("fd_max_gini", this.value);
  });

  function percentileNearestRank(sortedAsc, p) {
    var n = sortedAsc.length;
    if (n === 0) return null;
    var idx = Math.max(0, Math.min(n - 1, Math.ceil(p * n) - 1));
    return sortedAsc[idx];
  }

  // Service Rate denominator = requests_arrived (assigned+declined+infeasible
  // are mutually exclusive per request -- see OPERATOR_CONTROL_ROOM_PLAN.md).
  function updateServiceHealth(batch) {
    var requestsArrived = batch.requests_arrived;
    var assigned = batch.assigned, declined = batch.declined, infeasible = batch.infeasible_requests.length;
    var serviceRate = requestsArrived > 0 ? assigned / requestsArrived : null;
    document.getElementById("svcRateVal").textContent = serviceRate === null ? "--" : (serviceRate * 100).toFixed(1) + "%";
    var bar = document.getElementById("svcRateBar");
    bar.style.width = (serviceRate === null ? 0 : serviceRate * 100) + "%";
    bar.className = "progress-fill" + (serviceRate !== null && serviceRate < MIN_SERVICE_RATE ? " bad" : "");
    document.getElementById("svcAssigned").textContent = assigned;
    document.getElementById("svcDeclined").textContent = declined;
    document.getElementById("svcInfeasible").textContent = infeasible;

    var etas = batch.assignments.map(function (a) { return a.pickup_eta_seconds; }).sort(function (a, b) { return a - b; });
    var etaAvg = etas.length ? etas.reduce(function (a, b) { return a + b; }, 0) / etas.length : null;
    var etaP90 = percentileNearestRank(etas, 0.9);
    var etaWorst = etas.length ? etas[etas.length - 1] : null;
    document.getElementById("etaAvg").textContent = etaAvg === null ? "--" : (etaAvg / 60).toFixed(1) + "m";
    document.getElementById("etaP90").textContent = etaP90 === null ? "--" : (etaP90 / 60).toFixed(1) + "m";
    document.getElementById("etaWorst").textContent = etaWorst === null ? "--" : (etaWorst / 60).toFixed(1) + "m";

    var demand = requestsArrived;
    var supply = batch.feasible_drivers_unique;
    document.getElementById("demandVal").textContent = demand;
    document.getElementById("supplyVal").textContent = supply;
    var ratio = supply > 0 ? demand / supply : (demand > 0 ? Infinity : null);
    var ratioEl = document.getElementById("ratioVal");
    var statusEl = document.getElementById("ratioStatus");
    if (ratio === null) { ratioEl.textContent = "--"; statusEl.textContent = ""; }
    else if (!isFinite(ratio)) {
      ratioEl.textContent = "N/A / ∞";
      statusEl.innerHTML = "<b style='color:var(--bad);'>SUPPLY SHORTAGE</b> &mdash; 0 driver khả dụng cho " + demand + " request.";
    } else {
      ratioEl.textContent = ratio.toFixed(2) + "×";
      statusEl.innerHTML = ratio > SHORTAGE_RATIO_THRESHOLD
        ? "<b style='color:var(--bad);'>SUPPLY SHORTAGE</b>"
        : "<span style='color:var(--good);'>Supply đủ</span>";
    }
    return { serviceRate: serviceRate, etaP90: etaP90, demand: demand, supply: supply, ratio: ratio };
  }

  // Top/Bottom 10% computed from the CURRENT batch's real driver incomes
  // (r.drivers[].income) -- if bottom 10% average is $0, show N/A/∞ rather
  // than a fake finite ratio.
  function updateFairnessSummary(batch) {
    var incomes = batch.drivers.map(function (d) { return d.income; }).sort(function (a, b) { return a - b; });
    var n = incomes.length;
    var mean = n ? incomes.reduce(function (a, b) { return a + b; }, 0) / n : null;
    var bucket = Math.max(1, Math.ceil(n * 0.1));
    var bottom = n ? incomes.slice(0, bucket) : [];
    var top = n ? incomes.slice(n - bucket) : [];
    var bottomAvg = bottom.length ? bottom.reduce(function (a, b) { return a + b; }, 0) / bottom.length : null;
    var topAvg = top.length ? top.reduce(function (a, b) { return a + b; }, 0) / top.length : null;
    document.getElementById("fairMean").textContent = mean === null ? "--" : fmtMoney(mean);
    document.getElementById("fairBottom10").textContent = bottomAvg === null ? "--" : fmtMoney(bottomAvg);
    document.getElementById("fairTop10").textContent = topAvg === null ? "--" : fmtMoney(topAvg);
    var ratioEl = document.getElementById("fairRatio");
    if (bottomAvg === null || topAvg === null) ratioEl.textContent = "--";
    else if (bottomAvg === 0) ratioEl.textContent = topAvg > 0 ? "N/A / ∞" : "N/A";
    else ratioEl.textContent = (topAvg / bottomAvg).toFixed(2) + "×";

    var gini = batch.metrics.gini;
    var maxGini = parseFloat(document.getElementById("maxGiniInput").value);
    if (isNaN(maxGini)) maxGini = 0.25;
    var alertEl = document.getElementById("fairAlertLine");
    alertEl.innerHTML = gini > maxGini
      ? "<b style='color:var(--bad);'>&#9888; FAIRNESS LIMIT EXCEEDED</b> &mdash; Gini " + fmtNum(gini, 3) + " > " + fmtNum(maxGini, 3)
      : "<span style='color:var(--good);'>Trong ngưỡng đã đặt (&le; " + fmtNum(maxGini, 3) + ")</span>";
    return { gini: gini, maxGini: maxGini };
  }

  function evaluateAlerts(svc, fair) {
    var alerts = [];
    if (svc.serviceRate !== null && svc.serviceRate < MIN_SERVICE_RATE) {
      alerts.push({ sev: "warning", title: "Tỷ lệ phục vụ dưới ngưỡng", detail: (svc.serviceRate * 100).toFixed(1) + "% < " + (MIN_SERVICE_RATE * 100) + "%" });
    }
    if (svc.etaP90 !== null && svc.etaP90 > MAX_PICKUP_P90_SEC) {
      alerts.push({ sev: "warning", title: "ETA đón P90 vượt ngưỡng", detail: (svc.etaP90 / 60).toFixed(1) + "m > " + (MAX_PICKUP_P90_SEC / 60) + "m" });
    }
    if (fair.gini > fair.maxGini) {
      alerts.push({ sev: "critical", title: "Gini above fairness guardrail", detail: fmtNum(fair.gini, 3) + " > " + fmtNum(fair.maxGini, 3) });
    }
    if (svc.ratio !== null && !isFinite(svc.ratio)) {
      alerts.push({ sev: "critical", title: "Không có tài xế khả thi", detail: svc.demand + " request, 0 driver khả dụng" });
    } else if (svc.ratio !== null && svc.ratio > SHORTAGE_RATIO_THRESHOLD) {
      alerts.push({ sev: "warning", title: "Thiếu hụt nguồn cung so với nhu cầu", detail: svc.ratio.toFixed(2) + "× (demand " + svc.demand + " / supply " + svc.supply + ")" });
    }
    var list = document.getElementById("alertsList");
    if (!alerts.length) {
      list.innerHTML = "<div class='alert-item'><span class='alert-dot ok'></span><div><div class='title'>Tất cả trong ngưỡng</div>" +
        "<div class='detail'>Tỷ lệ phục vụ / ETA / Công bằng / Nguồn cung đều đạt ngưỡng hiện tại.</div></div></div>";
      return;
    }
    list.innerHTML = alerts.map(function (a) {
      return "<div class='alert-item'><span class='alert-dot " + a.sev + "'></span><div><div class='title'>" + a.title + "</div>" +
        "<div class='detail'>" + a.detail + "</div></div></div>";
    }).join("");
  }

  function setTopbarChips(policy, batch, status) {
    var cp = document.getElementById("chipPolicy"), cb = document.getElementById("chipBatch"), cs = document.getElementById("chipStatus");
    cp.style.display = cb.style.display = cs.style.display = "inline-block";
    cp.querySelector("b").textContent = policy;
    cb.querySelector("b").textContent = batch;
    cs.querySelector("b").textContent = status;
  }

  function setControlsForActiveRun(hasRun, isDone) {
    elStep.disabled = !hasRun || isDone || stepFetchInFlight || autoRunning;
    elRun.disabled = !hasRun || isDone || autoRunning || stepFetchInFlight;
    elPause.disabled = !autoRunning;
    elReset.disabled = !hasRun;
  }

  function hardResetPlayback() {
    runGeneration++;
    autoRunning = false;
    stepFetchInFlight = false;
    playback.running = false;
    playback.simTime = null;
    playback.stepTarget = null;
    playback.buffering = false;
    playback.lastWallMs = null;
    engineQ = { done: false, producerBusy: false, queue: [] };
    activeTrips.forEach(function (trip) { removeTripLayers(trip); });
    activeTrips.clear();
    activeTripByDriver.clear();
    historyTrail.forEach(function (item) { removeTripLayers(item.trip); });
    historyTrail = [];
    driverMarkers.forEach(function (m) { mapLayers.driver.removeLayer(m); });
    driverMarkers.clear();
    clearAllTrackedDrivers(); // §12: never carry tracked driver IDs across Reset/New Run
    latestDriverState.clear();
    ephemeralRequests.forEach(function (item) { item.layer.removeLayer(item.marker); });
    ephemeralRequests = [];
    servedEngineTotal = 0;
    clearAssignmentSelection();
    clearAssignTableRows();
    clearKpi();
    document.getElementById("statusGrid").style.display = "none";
    document.getElementById("bufferingBadge").style.display = "none";
    document.getElementById("alertsList").innerHTML = "<div class='empty'>Chưa có dữ liệu batch nào.</div>";
    document.getElementById("svcRateVal").textContent = "--";
    document.getElementById("svcRateBar").style.width = "0%";
    document.getElementById("demandVal").textContent = "--";
    document.getElementById("supplyVal").textContent = "--";
    document.getElementById("ratioVal").textContent = "--";
    document.getElementById("ratioStatus").textContent = "";
    document.getElementById("fairMean").textContent = "--";
    document.getElementById("fairBottom10").textContent = "--";
    document.getElementById("fairTop10").textContent = "--";
    document.getElementById("fairRatio").textContent = "--";
    document.getElementById("fairAlertLine").textContent = "";
  }

  elNewRun.addEventListener("click", async function () {
    hardResetPlayback();
    var timeFilter = getTimeFilterPayload(), dayFilter = getDayFilterPayload();
    var body = {
      policy: elPolicySelect.value,
      n_drivers: parseInt(document.getElementById("cfgDrivers").value, 10) || 200,
      lam: parseFloat(document.getElementById("cfgLam").value),
      gamma: parseFloat(document.getElementById("cfgGamma").value) || 0.9,
      alpha: parseFloat(document.getElementById("cfgAlpha").value) || 0.1,
      forecast_on: document.getElementById("cfgForecast").checked,
      seed: parseInt(document.getElementById("cfgSeed").value, 10) || 20260721,
      request_limit: parseInt(document.getElementById("cfgLimit").value, 10) || 3000,
      dataset: "val",
      time_filter: timeFilter, day_filter: dayFilter,
    };
    elNewRun.disabled = true;
    elBatchLine.textContent = "Đang tạo run + load dữ liệu thật (val.parquet)...";
    try {
      var res = await api("/simulations", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
      currentRunId = res.run_id;
      t0EpochSeconds = res.config.t0_epoch_seconds;
      var actualNote = res.note ? " -- " + res.note : "";
      elRunIdLabel.textContent = res.run_id + " · " + body.policy + " · " + res.config.n_drivers_actual + " drivers · " + res.total_requests + " request";
      elBatchLine.textContent = "Run " + res.run_id + " sẵn sàng (" + res.total_requests + " request thật từ val.parquet)." + actualNote;
      setTopbarChips(body.policy, "0", "ready");

      document.getElementById("crGrid").style.display = "grid";
      document.getElementById("crPolicy").textContent = body.policy;
      document.getElementById("crObjective").textContent = currentObjectiveLabel();
      document.getElementById("crDrivers").textContent = res.config.n_drivers_actual;
      document.getElementById("crForecast").textContent = body.forecast_on ? "ON" : "OFF";
      var filteredCount = res.config.filtered_request_count, availableCount = res.config.available_request_count;
      document.getElementById("crSlice").textContent = res.total_requests.toLocaleString("en-US") +
        " dùng / " + (filteredCount || res.total_requests).toLocaleString("en-US") + " khớp scenario / " +
        (availableCount || 195508).toLocaleString("en-US") + " tổng";
      if (res.constants) {
        document.getElementById("advEtaThreshold").textContent = res.constants.eta_threshold_seconds + " sec · fixed";
        document.getElementById("advBatchWindow").textContent = res.constants.batch_window_seconds + " sec · fixed";
        document.getElementById("advDeadheadCost").textContent = "$" + res.constants.deadhead_cost_per_second_usd + "/s · fixed";
      }

      lastRunConfig = { policy: body.policy, objective: currentObjectiveLabel(), n_drivers: res.config.n_drivers_actual,
        forecast_on: body.forecast_on, lam: body.lam, gamma: body.gamma, alpha: body.alpha, seed: body.seed,
        dataset: body.dataset, request_limit: body.request_limit, time_filter: timeFilter, day_filter: dayFilter };
      lastBatchMetrics = null;
      document.getElementById("btnSaveRun").disabled = false;
      document.getElementById("saveRunResult").textContent = "";

      ensureLoopStarted();
      setControlsForActiveRun(true, false);
    } catch (e) {
      elBatchLine.textContent = "Lỗi tạo run: " + e.message;
    }
    elNewRun.disabled = false;
  });

  elStep.addEventListener("click", async function () {
    if (stepFetchInFlight || autoRunning || !currentRunId) return;
    stepFetchInFlight = true;
    setControlsForActiveRun(true, false);
    try {
      await ensureOneQueuedBatch();
      if (playback.simTime === null && engineQ.queue.length === 0) {
        elBatchLine.textContent = "Hết dữ liệu để advance thêm.";
        return;
      }
      // Advance the global clock by exactly one 60s simulation window --
      // NOT "wait until every trip that started this batch finishes"
      // (spec 48/49). Trips longer than 60s simply keep moving on the next Step.
      playback.stepTarget = (playback.simTime || 0) + WINDOW_SECONDS;
      playback.running = true;
      ensureLoopStarted();
      while (playback.running) { await sleep(30); } // resolves once the loop hits stepTarget
      setTopbarChips(elPolicySelect.value, String(lastActivatedBatchNumber()), engineQ.done && !activeTrips.size ? "done" : "paused");
    } finally {
      stepFetchInFlight = false;
      setControlsForActiveRun(true, engineQ.done && engineQ.queue.length === 0);
    }
  });

  function lastActivatedBatchNumber() {
    var max = 0;
    activeTrips.forEach(function (t) { if (t.batch > max) max = t.batch; });
    historyTrail.forEach(function (item) { if (item.trip.batch > max) max = item.trip.batch; });
    return max;
  }

  elRun.addEventListener("click", async function () {
    if (autoRunning) return;
    autoRunning = true;
    playback.running = true;
    ensureLoopStarted();
    setControlsForActiveRun(true, false);
    setTopbarChips(elPolicySelect.value, String(lastActivatedBatchNumber()), "running");
    pumpEngine(runGeneration); // fire-and-forget: keeps buffer filled while autoRunning
    // Watch for natural completion (engine done + no more active trips) to re-enable controls.
    while (autoRunning) {
      await sleep(200);
      if (engineQ.done && engineQ.queue.length === 0 && activeTrips.size === 0) {
        autoRunning = false;
        playback.running = false;
        setTopbarChips(elPolicySelect.value, String(lastActivatedBatchNumber()), "done");
      }
    }
    setControlsForActiveRun(!!currentRunId, engineQ.done && engineQ.queue.length === 0 && activeTrips.size === 0);
  });

  elPause.addEventListener("click", function () {
    autoRunning = false;
    playback.running = false;
    setTopbarChips(elPolicySelect.value, String(lastActivatedBatchNumber()), "paused");
    setControlsForActiveRun(!!currentRunId, false);
  });

  elReset.addEventListener("click", async function () {
    if (!currentRunId) return;
    elReset.disabled = true;
    try {
      await api("/simulations/" + currentRunId + "/reset", { method: "POST" });
      hardResetPlayback();
      elBatchLine.textContent = "Đã reset run " + currentRunId + ".";
      setTopbarChips(elPolicySelect.value, "0", "ready");
      ensureLoopStarted();
      // P0.3 fix (kept): Reset must fully re-enable Step/Run even after done.
      setControlsForActiveRun(true, false);
    } catch (e) {
      elBatchLine.textContent = "Lỗi reset: " + e.message;
      elReset.disabled = false;
    }
  });

  function clearKpi() {
    ["kpiUtility", "kpiServed", "kpiAvgIncome", "kpiDeadhead"].forEach(function (id) {
      document.getElementById(id).textContent = "--";
    });
    document.getElementById("histBars").innerHTML = "";
    document.querySelector("#lorenzWrap svg").innerHTML = "";
    setGiniGauge(null);
  }

  function renderKpi(m) {
    document.getElementById("kpiUtility").textContent = fmtMoney(m.utility);
    document.getElementById("kpiServed").textContent = m.served_total;
    document.getElementById("kpiAvgIncome").textContent = fmtMoney(m.avg_income);
    document.getElementById("kpiDeadhead").textContent = "$" + fmtNum(m.avg_deadhead_cost, 3);
    setGiniGauge(m.gini);
  }

  // ---- gauge donut, ported visual from demo_fairdispatch's Gini gauge,
  // driven by the real metrics.gini value on each ACTIVATED batch (not
  // every rAF frame -- see spec 66/67, KPI/chart updates only on visible
  // batch activation, never at prefetch time).
  var GAUGE_CIRC = 2 * Math.PI * 28; // r=28
  function setGiniGauge(gini) {
    var circle = document.getElementById("giniGauge");
    var text = document.getElementById("giniGaugeText");
    if (gini === null || gini === undefined || isNaN(gini)) {
      circle.setAttribute("stroke-dasharray", "0 " + GAUGE_CIRC);
      text.textContent = "--";
      return;
    }
    var frac = Math.min(1, Math.max(0, gini));
    circle.setAttribute("stroke-dasharray", (frac * GAUGE_CIRC).toFixed(1) + " " + GAUGE_CIRC.toFixed(1));
    text.textContent = fmtNum(gini, 3);
  }

  // P0.6 (kept): real histogram from backend-computed bins over actual driver incomes.
  function renderHistogram(hist) {
    var wrap = document.getElementById("histBars");
    wrap.innerHTML = "";
    if (!hist || !hist.counts || !hist.counts.length) return;
    var maxCount = Math.max.apply(null, hist.counts) || 1;
    hist.counts.forEach(function (c, i) {
      var bar = document.createElement("div");
      bar.className = "bar";
      bar.style.height = Math.max(2, (c / maxCount) * 100) + "%";
      bar.title = "$" + fmtNum(hist.bins[i], 0) + " - $" + fmtNum(hist.bins[i + 1], 0) + ": " + c + " driver";
      wrap.appendChild(bar);
    });
  }

  // P2.5 (kept): Lorenz curve from real driver incomes returned each step.
  function renderLorenz(points) {
    var svg = document.querySelector("#lorenzWrap svg");
    if (!points || !points.length) { svg.innerHTML = ""; return; }
    var W = 200, H = 100, pad = 4;
    function px(x) { return pad + x * (W - 2 * pad); }
    function py(y) { return (H - pad) - y * (H - 2 * pad); }
    var path = points.map(function (p, i) { return (i === 0 ? "M" : "L") + px(p.x).toFixed(1) + "," + py(p.y).toFixed(1); }).join(" ");
    var diag = "M" + px(0) + "," + py(0) + " L" + px(1) + "," + py(1);
    svg.innerHTML =
      '<line x1="' + px(0) + '" y1="' + py(0) + '" x2="' + px(1) + '" y2="' + py(0) + '" stroke="#E5E7EB"/>' +
      '<line x1="' + px(0) + '" y1="' + py(1) + '" x2="' + px(0) + '" y2="' + py(0) + '" stroke="#E5E7EB"/>' +
      '<path d="' + diag + '" stroke="#D1D5DB" stroke-dasharray="3,3" fill="none"/>' +
      '<path d="' + path + '" stroke="#17365D" stroke-width="1.6" fill="none"/>';
  }

  async function explainAssignment(reqIdx, batch) {
    var empty = document.getElementById("trackerEmpty");
    var body = document.getElementById("trackerBody");
    empty.style.display = "none";
    body.style.display = "block";
    body.innerHTML = "<div class='loading'>Đang tính lại score thật từ policy engine...</div>";
    try {
      var r = await api("/simulations/" + currentRunId + "/explain/" + reqIdx + "?batch=" + batch);
      var trip = findTrip(reqIdx);
      var html = "<div class='route'>Request #" + r.request.req_idx + " &middot; zone " + r.request.pickup_zone +
        " &rarr; " + r.request.dropoff_zone + " &middot; batch #" + batch + "</div>";
      html += "<div class='fare'>" + fmtMoney(r.request.fare) + " <small>fare</small></div>";
      if (trip) {
        var phaseLabel = trip.phase === "deadhead" ? "Đang tới điểm đón" : trip.phase === "onboard" ? "Đang chở khách" : "Đã hoàn tất chuyến";
        var pct = trip.phase === "deadhead"
          ? (trip.pickupSim > trip.startSim ? clamp01((playback.simTime - trip.startSim) / (trip.pickupSim - trip.startSim)) : 1)
          : trip.phase === "onboard"
            ? (trip.dropoffSim > trip.pickupSim ? clamp01((playback.simTime - trip.pickupSim) / (trip.dropoffSim - trip.pickupSim)) : 1)
            : 1;
        html += "<div class='qrow' style='border-top:none;'><span>Giai đoạn hiển thị: <b>" + phaseLabel + "</b></span><b>" + Math.round(pct * 100) + "%</b></div>";
      }
      if (r.selected_local_rank && r.selected_local_rank > 1) {
        html += "<div class='badge-global'>GLOBAL OPTIMUM</div>" +
          "<div class='rank-note'>Driver #" + r.selected_driver_id + " không có local score cao nhất cho request này " +
          "(local rank #" + r.selected_local_rank + "), nhưng được <b>Hungarian</b> chọn để tối ưu tổng điểm cả batch.</div>";
      }
      var maxAbs = 1;
      r.candidates.forEach(function (c) { maxAbs = Math.max(maxAbs, Math.abs(c.final_score || 0)); });
      r.candidates.forEach(function (c) {
        // P0.1 fix (kept): winner = c.is_selected (the REAL Hungarian
        // outcome stored server-side), never just index 0 / max score.
        var isWinner = !!c.is_selected;
        html += "<div class='qrow'" + (isWinner ? " style='border-top:2px solid var(--good);'" : "") + ">" +
          "<span>" + (isWinner ? "&#10003; Driver #" + c.driver_id + " (selected)" : "Driver #" + c.driver_id + " (rank #" + c.local_rank + ")") +
          "</span><b>" + fmtNum(c.final_score, 2) + "</b></div>";
        if (isWinner) {
          html += "<div style='margin:4px 0 8px;font-size:11px;color:var(--gray);'>ETA " + fmtNum(c.eta_seconds, 0) +
            "s &middot; income $" + fmtNum(c.driver_income, 2) + "</div>";
          if (c.formula) {
            html += "<div class='hint' style='margin:2px 0 8px;'>" + c.formula + "</div>";
          } else {
            html += scoreBar("Giá trị tức thời", c.immediate_utility, maxAbs);
            html += scoreBar("Giá trị khu vực tương lai", c.future_zone_value, maxAbs);
            html += scoreBar("Điều chỉnh công bằng", c.fairness_adjustment, maxAbs);
          }
        }
      });
      body.innerHTML = html;
    } catch (e) {
      body.innerHTML = "<div class='errbox'>" + e.message + "</div>";
    }
  }

  function scoreBar(label, val, maxAbs) {
    var pct = Math.min(100, Math.abs(val) / maxAbs * 100);
    var neg = val < 0;
    return "<div class='score-bar-row'><span class='lab'>" + label + "</span>" +
      "<div class='track'><div class='fill" + (neg ? " neg" : "") + "' style='width:" + pct.toFixed(1) + "%'></div></div>" +
      "<span class='val'>" + fmtNum(val, 2) + "</span></div>";
  }

  // ======================================================================
  // COMPARE POLICIES (unchanged -- no continuous-playback concerns here)
  // ======================================================================
  var compareLoaded = false;

  async function loadCompare() {
    compareLoaded = true;
    try {
      var r = await api("/replay/ablation");
      document.getElementById("compareSource").textContent = "Nguồn: " + r.source + " (5 seed, 195,508 request/seed)";
      var cards = document.getElementById("compareCards");
      var byName = {};
      r.rows.forEach(function (row) { byName[row.ablation] = row; });
      var order = [["full", "MOMAQL đầy đủ", "full"], ["no_forecast", "Không dự báo", "noforecast"], ["no_fairness", "Không công bằng", "nofairness"]];
      cards.innerHTML = "";
      order.forEach(function (o) {
        var row = byName[o[0]];
        if (!row) return;
        var div = document.createElement("div");
        div.className = "compare-card " + o[2];
        div.innerHTML = "<h3>" + o[1] + "</h3>" +
          "<div class='n'>" + fmtMoney(parseFloat(row.utility_mean)) + "</div><div class='l'>Hiệu quả</div>" +
          "<div class='n' style='margin-top:8px;'>" + fmtNum(parseFloat(row.gini_mean), 3) + "</div><div class='l'>Gini (thấp hơn = công bằng hơn)</div>";
        cards.appendChild(div);
      });
      var full = byName["full"], nf = byName["no_forecast"];
      if (full && nf) {
        var diff = ((parseFloat(full.utility_mean) - parseFloat(nf.utility_mean)) / parseFloat(nf.utility_mean) * 100).toFixed(1);
        document.getElementById("tradeoffLine").innerHTML =
          "Đầy đủ: <b>+" + diff + "% Hiệu quả</b> so với Không dự báo &nbsp;&middot;&nbsp; Không dự báo: <b>Gini thấp hơn (công bằng hơn)</b> &mdash; đây là trade-off, không phải phương án Đầy đủ thắng tuyệt đối.";
      }
    } catch (e) {
      document.getElementById("compareSource").textContent = "Lỗi tải replay: " + e.message;
    }
  }

  document.getElementById("btnLiveCompare").addEventListener("click", async function () {
    var out = document.getElementById("liveCompareResult");
    var btn = document.getElementById("btnLiveCompare");
    btn.disabled = true;
    out.innerHTML = "<div class='loading'>Đang chạy Đầy đủ...<br>Đang chạy Không dự báo...</div>";
    var t0 = performance.now();
    try {
      var r = await api("/compare/live", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ n_drivers: 100, seed: 20260721, lam: 0.5, request_limit: 1500 }),
      });
      var f = r.results.full, nf = r.results.no_forecast;
      out.innerHTML = "<p class='hint'>" + r.note + " (" + ((performance.now() - t0) / 1000).toFixed(1) + "s)</p><div class='compare-cards'>" +
        "<div class='compare-card full'><h3>Đầy đủ (trực tiếp)</h3><div class='n'>" + fmtMoney(f.utility) + "</div><div class='l'>Hiệu quả</div><div class='n' style='margin-top:8px;'>" + fmtNum(f.gini, 3) + "</div><div class='l'>Gini</div><div class='l' style='margin-top:6px;'>Đã phục vụ " + f.served + "/" + f.requests_used + " (" + f.n_drivers_actual + " tài xế)</div></div>" +
        "<div class='compare-card noforecast'><h3>Không dự báo (trực tiếp)</h3><div class='n'>" + fmtMoney(nf.utility) + "</div><div class='l'>Hiệu quả</div><div class='n' style='margin-top:8px;'>" + fmtNum(nf.gini, 3) + "</div><div class='l'>Gini</div><div class='l' style='margin-top:6px;'>Đã phục vụ " + nf.served + "/" + nf.requests_used + " (" + nf.n_drivers_actual + " tài xế)</div></div>" +
        "</div>";
    } catch (e) {
      out.innerHTML = "<div class='errbox'>So sánh nhanh trực tiếp thất bại<br>" + e.message + "</div>";
    }
    btn.disabled = false;
  });

  // ======================================================================
  // LONG-HORIZON (unchanged)
  // ======================================================================
  var horizonLoaded = false;
  var horizonAgg = null;
  var DAYS = [1, 2, 3, 4, 5, 6, 7, 14, 21, 28, 37];

  async function loadHorizon() {
    horizonLoaded = true;
    try {
      var r = await api("/replay/long_horizon");
      var sums = {};
      r.rows.forEach(function (row) {
        if (row.config !== "full" && row.config !== "no_forecast") return;
        var key = row.horizon_day + "|" + row.config;
        if (!sums[key]) sums[key] = { u: [], g: [] };
        sums[key].u.push(parseFloat(row.utility));
        sums[key].g.push(parseFloat(row.gini));
      });
      horizonAgg = {};
      DAYS.forEach(function (d) {
        horizonAgg[d] = {};
        ["full", "no_forecast"].forEach(function (cfg) {
          var s = sums[d + "|" + cfg];
          if (s) {
            horizonAgg[d][cfg] = {
              utility: s.u.reduce(function (a, b) { return a + b; }, 0) / s.u.length,
              gini: s.g.reduce(function (a, b) { return a + b; }, 0) / s.g.length,
            };
          }
        });
      });
      document.getElementById("daySlider").max = DAYS.length - 1;
      renderHorizonDay(0);
    } catch (e) {
      document.getElementById("horizonCards").innerHTML = "<div class='errbox'>" + e.message + "</div>";
    }
  }

  document.getElementById("daySlider").addEventListener("input", function (e) {
    renderHorizonDay(parseInt(e.target.value, 10));
  });

  function renderHorizonDay(idx) {
    var day = DAYS[idx];
    var data = horizonAgg ? horizonAgg[day] : null;
    var cards = document.getElementById("horizonCards");
    if (!data || !data.full || !data.no_forecast) { cards.innerHTML = "<p class='hint'>Không có dữ liệu cho ngày " + day + ".</p>"; return; }
    var utilDiff = ((data.full.utility - data.no_forecast.utility) / data.no_forecast.utility * 100).toFixed(2);
    cards.innerHTML =
      "<div class='compare-card full'><h3>Đầy đủ &mdash; Ngày " + day + "</h3><div class='n'>" + fmtMoney(data.full.utility) + "</div><div class='l'>Hiệu quả</div><div class='n' style='margin-top:8px;'>" + fmtNum(data.full.gini, 4) + "</div><div class='l'>Gini</div></div>" +
      "<div class='compare-card noforecast'><h3>Không dự báo &mdash; Ngày " + day + "</h3><div class='n'>" + fmtMoney(data.no_forecast.utility) + "</div><div class='l'>Hiệu quả</div><div class='n' style='margin-top:8px;'>" + fmtNum(data.no_forecast.gini, 4) + "</div><div class='l'>Gini</div></div>";
    var existing = document.getElementById("horizonDiffLine");
    var diffHtml = "Chênh lệch hiệu quả tại Ngày " + day + ": <b>" + (utilDiff >= 0 ? "+" : "") + utilDiff + "%</b> (Đầy đủ so với Không dự báo)";
    if (!existing) {
      var div = document.createElement("div");
      div.id = "horizonDiffLine";
      div.className = "tradeoff";
      div.innerHTML = diffHtml;
      cards.parentNode.insertBefore(div, cards.nextSibling);
    } else {
      existing.innerHTML = diffHtml;
    }
  }

  // ======================================================================
  // RUN HISTORY (unchanged)
  // ======================================================================
  async function loadHistory() {
    try {
      var r = await api("/simulations");
      var tbody = document.querySelector("#historyTable tbody");
      tbody.innerHTML = "";
      r.runs.forEach(function (run) {
        var tr = document.createElement("tr");
        var driversLabel = run.n_drivers_actual !== undefined && run.n_drivers_actual !== run.n_drivers_requested
          ? run.n_drivers_actual + " (yêu cầu " + run.n_drivers_requested + ")" : run.n_drivers_actual;
        tr.innerHTML = "<td>" + run.run_id + "</td><td>" + run.policy + "</td><td class='num'>" + driversLabel +
          "</td><td class='num'>" + run.lam + "</td><td>" + (run.forecast_on ? "ON" : "OFF") + "</td><td>" + run.status +
          "</td><td class='num'>" + (run.utility !== null ? fmtMoney(run.utility) : "--") + "</td><td class='num'>" +
          (run.gini !== null ? fmtNum(run.gini, 3) : "--") + "</td>";
        tbody.appendChild(tr);
      });
    } catch (e) {
      document.querySelector("#historyTable tbody").innerHTML = "<tr><td colspan='8' class='errbox'>" + e.message + "</td></tr>";
    }
  }

  // ======================================================================
  // PROVENANCE + BACKEND HEALTH (unchanged)
  // ======================================================================
  async function loadProvenance() {
    try {
      var r = await api("/provenance");
      document.getElementById("backendDot").className = "dot on";
      document.getElementById("backendLabel").textContent = "Máy chủ đã sẵn sàng";
      var valEntry = r.dataset_checksums && r.dataset_checksums["val.parquet"];
      var valSha = valEntry && valEntry.sha256 ? valEntry.sha256.slice(0, 16) + "..." : "Không có sẵn";
      var engineSha = (r.bundle_engine_source && r.bundle_engine_source.files["policies.py"] &&
        r.bundle_engine_source.files["policies.py"].sha256 || "Không có sẵn");
      var devHead = (r.dev_repo && r.dev_repo.git_head) ? r.dev_repo.git_head.slice(0, 10) : "Không có sẵn";
      var dirty = r.dev_repo && r.dev_repo.working_tree_dirty;
      document.getElementById("provenanceStrip").innerHTML =
        "<span>Ảnh chụp engine (SHA-256 policies.py): <b>" + (engineSha === "Không có sẵn" ? engineSha : engineSha.slice(0, 16) + "...") + "</b></span>" +
        "<span>SHA-256 bộ dữ liệu val.parquet: <b>" + valSha + "</b></span>" +
        "<span>Dev repo HEAD (chỉ nguồn dữ liệu): <b>" + devHead + (dirty ? " (working tree có thay đổi chưa commit)" : "") + "</b></span>";
    } catch (e) {
      document.getElementById("backendDot").className = "dot off";
      document.getElementById("backendLabel").textContent = "Backend không phản hồi";
      document.getElementById("provenanceStrip").textContent = "Không tải được provenance: " + e.message;
    }
  }

  initMap();
  loadProvenance();
})();
