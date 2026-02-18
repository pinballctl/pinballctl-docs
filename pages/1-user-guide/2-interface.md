# Interface Tour

This page gives you a quick tour of the Pinball CTL interface so you can find what you need fast.

## Login

Open Pinball CTL in your browser and sign in.

<img src="./media/screenshot-login.png" data-source='{"url":"/login","dark_mode":true}' alt="Pinball CTL login screen" style="width: 100%; max-width: 800px; height: auto;">

Default login credentials:

- Username: `admin`
- Password: `password`

Change the default password after your first login via `System -> Settings`.

## Dashboard Overview

After login, you land on the Dashboard. This is your at-a-glance machine status page.

<img src="./media/screenshot-dashboard.png" data-source='{"url":"/login","next_url":"/dashboard","dark_mode":true,"settle_ms":320,"click":[{"action":"type","selector":"input[name=\"username\"]","value":"admin"},{"action":"type","selector":"input[name=\"password\"]","value":"password"},{"action":"click","selector":"button[type=\"submit\"]","wait_for":"[data-menu-toggle]"}]}' alt="Pinball CTL dashboard" style="width: 100%; max-width: 800px; height: auto;">

The dashboard cards show key status areas such as Wi-Fi, bridge state, ESP32 connectivity, dependencies, uptime, and gameplay or machine metrics.

Use this page first when checking whether your system is healthy.

## Control Centre

Use the grid icon in the top bar to open the Control Centre. This is the main navigation hub for all areas.

<img src="./media/screenshot-control-center.png"
     data-source='{"url":"/login","dark_mode":true,"settle_ms":420,"click":[{"action":"type","selector":"input[name=\"username\"]","value":"admin"},{"action":"type","selector":"input[name=\"password\"]","value":"password"},{"action":"click","selector":"button[type=\"submit\"]","wait_for":"[data-menu-toggle]"},{"action":"click","selector":"[data-menu-toggle]","wait_for":"body.flood-open"},{"action":"wait","wait_for":"#flood-menu-body .flood-grid"}]}'
     alt="Pinball CTL control centre" style="width: 100%; max-width: 800px; height: auto;">

The Control Centre groups pages by purpose:

- Overview: high-level operational pages.
- Authoring: Rules, Lighting, and playfield-related work.
- Platform: hardware, firmware, and ESPLink.
- Operations: logs and service diagnostics.
- System: settings such as Wi-Fi and install-wide options.

## Search

Use the search box (top right of Control Centre) to filter the available pages.

<img src="./media/screenshot-control-center-search.png" data-source='{"url":"/login","dark_mode":true,"settle_ms":420,"click":[{"action":"type","selector":"input[name=\"username\"]","value":"admin"},{"action":"type","selector":"input[name=\"password\"]","value":"password"},{"action":"click","selector":"button[type=\"submit\"]","wait_for":"[data-menu-toggle]"},{"action":"click","selector":"[data-menu-toggle]","wait_for":"body.flood-open"},{"action":"wait","wait_for":"#flood-menu-body .flood-grid"}],"highlight":{"selector":".flood-menu-head-actions","style":"border: 4px solid red; border-radius: 8px;"}}' alt="Control Centre search box" style="width: 100%; max-width: 800px; height: auto;">

Search is best when you type the page name directly, for example: `lighting`, `rules`, or `hardware`, then click the page you want.

## Recently Visited

Pinball CTL keeps quick shortcuts so you can get back to pages you use most.

The Recently Visited row gives one-click access to pages you opened recently.

<img src="./media/screenshot-control-center-recent.png" data-source='{"url":"/login","dark_mode":true,"settle_ms":420,"click":[{"action":"type","selector":"input[name=\"username\"]","value":"admin"},{"action":"type","selector":"input[name=\"password\"]","value":"password"},{"action":"click","selector":"button[type=\"submit\"]","wait_for":"[data-menu-toggle]"},{"action":"click","selector":"[data-menu-toggle]","wait_for":"body.flood-open"},{"action":"click","selector":"[data-nav-link][data-module-name=\"rules\"]","wait_for":"h1"},{"action":"click","selector":"[data-menu-toggle]","wait_for":"body.flood-open"},{"action":"click","selector":"[data-nav-link][data-module-name=\"hardware\"]","wait_for":"h1"},{"action":"click","selector":"[data-menu-toggle]","wait_for":"body.flood-open"},{"action":"click","selector":"[data-nav-link][data-module-name=\"settings\"]","wait_for":"h1"},{"action":"click","selector":"[data-menu-toggle]","wait_for":"body.flood-open"},{"action":"wait","wait_for":".flood-recent"}],"highlight":{"selector":".flood-recent","style":"border: 4px solid red; border-radius: 8px; padding: 6px;"}}' alt="Recently visited pages" style="width: 100%; max-width: 800px; height: auto;">

## Bookmarks

When you hover over a link, a yellow bookmark icon appears.

Clicking the icon adds that link to the top bookmarks menu for faster access to frequently used areas.

You can also drag and drop items in the top bookmarks menu to arrange them in your preferred order.
