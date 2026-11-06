# Official firmware release (v1.0.0)

**Status:** not started. Begin once the prototype is validated (initial prototype roadmap, step 6) and a stable ESPHome release includes the `ld2460` component.

## Goal

Ship a first official firmware release that:

- meets every item on the [Made for ESPHome checklist](https://github.com/esphome/devices.esphome.io/blob/main/.github/made-for-esphome-checklist.md), and
- is built, packaged and published by GitHub Actions, so users get updates in Home Assistant through the `update.http_request` component.

## Starting point (firmware v0)

`firmware/presence.yaml` builds on ESPHome `2026.11.0b2` (pinned in `mise.toml`). It already has:

- `esphome.project`, `name_add_mac_suffix` and `dashboard_import`
- Wi-Fi with no credentials, `captive_portal`, `improv_serial` and `improv_ble`
- `api` with encryption but no key in the repo
- `ota: esphome`
- LD2460 sensors with throttle filters, and a template Presence sensor
- the BLE tracker and Bluetooth proxy

## Steps

### 1. Stable ESPHome

- [ ] Move `mise.toml` from the beta pin to the first stable ESPHome release that includes `ld2460`.
- [ ] Set that version as `esphome.min_version` in `presence.yaml`, and as the minimum ESPHome version in the README.
- [ ] Re-check every config key against the stable docs. Renamed keys to watch, for example: `esp32_improv` became `improv_ble` in 2026.10.

### 2. Close the checklist gaps

- [x] Give every entity and component an `id`, as the checklist requires (done in v0). Keep it true for every new entity, including those in add-on packages.
- [ ] Check that the project name has no "ESPHome" in it, except as a trailing "for ESPHome".
- [ ] Check that there are no `!secret`, passwords, `psk:` or static IPs anywhere, including in packages.
- [ ] Check that serial flashing stays enabled.
- [ ] Check that `package_import_url` resolves on `main`, with the exact case of each path.
- [ ] Check that the config is valid and compiles after adoption with no user changes. Adopt it into a clean ESPHome Builder as a test.
- [ ] Confirm that the add-on packages (light, CO₂) still work as opt-in includes after adoption.

### 3. Update entity and OTA over HTTP

- [ ] Add `http_request`, `ota: - platform: http_request` and `update: - platform: http_request`. The update entity points at the manifest URL on GitHub Pages. Take the keys from the docs for the pinned version.
- [ ] Decide how often devices check for updates, and whether updates install automatically (default: manual install from Home Assistant).
- [ ] Measure flash and RAM afterwards. v0 uses about 70% of the app partition, so check that two OTA slots still fit with the Bluetooth proxy and encryption.

### 4. GitHub Actions build and release

- [ ] Workflow on pull requests: `esphome config` and `esphome compile` for `presence.yaml` and for each add-on combination.
- [ ] Workflow on version tags (`v*`):
  - [ ] Build with ESPHome's official build action, or with the reusable workflows ESPHome publishes. Pin the action versions.
  - [ ] Take `project_version` from the tag, so the device reports the release it runs.
  - [ ] Attach the first-flash image (`factory.bin`), the OTA image (`ota.bin`) and the manifest to the GitHub Release.
  - [ ] Publish the manifest and images to GitHub Pages at one fixed URL, used by both the web installer and the update entity.
- [ ] Decide whether prereleases (`v*-beta*`) publish to a separate manifest, for testers.

### 5. Web installer and documentation

- [ ] Add an ESP Web Tools install page in `docs/`, served from GitHub Pages and fed by the same manifest.
- [ ] README: install with the web installer, adopt in ESPHome Builder, update from Home Assistant, Bermuda setup, minimum ESPHome version, and changelog location.
- [ ] Release notes template (for example `.github/release.yml`), or a `CHANGELOG.md`.

### 6. Release

- [ ] Test a full OTA cycle: flash a pre-release build, publish a newer tag, and update from Home Assistant.
- [ ] Tag `v1.0.0`.
- [ ] Submit the device to devices.esphome.io using the Made for ESPHome checklist.

## Open questions

- **Versioning:** SemVer tags (`v1.0.0`) or ESPHome-style date versions? `esphome.project.version` accepts any string.
- **Builds per add-on:** one firmware with every add-on built in (it detects missing I²C sensors at runtime), or one build per combination? This affects the manifest layout and flash size.
- **Partition table:** is the default enough, or does the S3's 8 MB flash call for a custom table with larger OTA slots?
- **API key on update:** do devices updated over HTTP keep the key set at adoption? Confirm that an update never wipes it.
- **Future C6 board:** a second board package means a second manifest, or a multi-chip manifest. Keep the workflow parameterized by board.
