"""Static regression guard for multi-driver tracking. Real interactive
verification (add/remove/switch camera target, coexistence with Request
selection, the 10-driver limit, Reset/New Run clearing everything) was done
with Playwright in a real browser -- not repeated here as string checks.
This file only guards the specific structural invariants: a dedicated
searchFocus layer never touched by syncIdleDrivers()'s per-batch tooltip
rebind, and Map-keyed per-driver state (no reintroduction of a single
trackedDriverId that would silently drop back to one-driver tracking)."""
from __future__ import annotations

from pathlib import Path

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
APP_JS = (FRONTEND_DIR / "app.js").read_text(encoding="utf-8")
INDEX_HTML = (FRONTEND_DIR / "index.html").read_text(encoding="utf-8")


def test_multi_driver_state_is_map_keyed_not_single_id():
    assert "var trackedDrivers = new Map();" in APP_JS
    assert "var cameraTargetDriverId = null;" in APP_JS
    # the old single-driver design must not have crept back in
    assert "var trackedDriverId = null;" not in APP_JS
    assert "var trackedFocusMarker = null;" not in APP_JS


def test_max_tracked_drivers_limit_and_vietnamese_guard_message():
    assert "var MAX_TRACKED_DRIVERS = 10;" in APP_JS
    assert "tối đa " in APP_JS and "tài xế cùng lúc" in APP_JS


def test_dedicated_search_focus_layer_not_shared_with_driver_layer():
    assert 'mapLayers.searchFocus = L.layerGroup().addTo(leafletMap);' in APP_JS


def test_state_cached_before_active_trip_early_return():
    idx_cache = APP_JS.index("latestDriverState.set(d.driver_id, d);")
    idx_skip = APP_JS.index("if (activeTripByDriver.has(d.driver_id)) return;")
    assert idx_cache < idx_skip


def test_search_adds_or_focuses_not_one_shot_open_tooltip():
    assert "addOrFocusTrackedDriver(id)" in APP_JS
    assert "m.openTooltip();" not in APP_JS


def test_frame_and_batch_update_hooks_wired_for_all_tracked():
    assert "updateAllTrackedDriversFocus(nowMs);" in APP_JS  # playbackLoop, every rAF frame
    assert "updateAllTrackedDriversFocus(performance.now());" in APP_JS  # activateBatch


def test_reset_and_new_run_clear_all_tracking():
    idx_clear = APP_JS.index("clearAllTrackedDrivers(); // §12")
    idx_marker_clear = APP_JS.index("driverMarkers.clear();")
    assert idx_clear > 0
    assert abs(idx_clear - idx_marker_clear) < 500


def test_request_selection_no_longer_clears_driver_tracking():
    # coexistence requirement: opening a Request explanation must NOT wipe
    # trackedDrivers (the previous single-driver task's mutual-exclusion
    # rule was explicitly reversed by this follow-up)
    assert "clearAllTrackedDrivers();" not in APP_JS.split("async function toggleAssignmentSelection")[1].split("\n\n")[0]


def test_remove_one_and_clear_all_present():
    assert "function removeTrackedDriver(driverId)" in APP_JS
    assert "function clearAllTrackedDrivers()" in APP_JS
    assert "function setCameraTarget(driverId)" in APP_JS


def test_tracking_panel_ui_present_and_vietnamese():
    assert 'id="trackingPanel"' in INDEX_HTML
    assert 'id="trackingChips"' in INDEX_HTML
    assert 'id="btnUntrackAll"' in INDEX_HTML
    assert ">Ngừng theo dõi tất cả<" in INDEX_HTML
    assert "Đang theo dõi" in INDEX_HTML
