(() => {
  const mounts = document.querySelectorAll("[data-taba-table-visualizer]");
  if (!mounts.length) return;

  const seedRegions = [
    {
      id: "r1",
      key: "token admission",
      region: "a",
      oldValue: "allow",
      guard: true,
      replacement: "quarantine",
      guardText: "inside G: provenance sentence holds",
    },
    {
      id: "r2",
      key: "token admission",
      region: "a'",
      oldValue: "allow",
      guard: false,
      replacement: "quarantine",
      guardText: "outside G: provenance sentence does not hold",
    },
    {
      id: "r3",
      key: "oracle risk",
      region: "b",
      oldValue: "watch",
      guard: true,
      replacement: "freeze",
      guardText: "inside G: oracle-risk sentence holds",
    },
    {
      id: "r4",
      key: "incident memory",
      region: "c",
      oldValue: "clear",
      guard: false,
      replacement: "flagged",
      guardText: "outside G: incident sentence does not hold",
    },
  ];

  const cloneSeed = () => seedRegions.map((region) => ({ ...region }));

  function initVisualizer(mount, index) {
    let regions = cloneSeed();
    let selectedId = regions[0].id;
    let appliedCount = 0;
    let splitCounter = 0;
    let playTimer = null;

    const root = document.createElement("section");
    root.className = "taba-viz";
    root.setAttribute("aria-label", "Interactive safe table revision visualizer");
    root.innerHTML = `
      <div class="taba-viz-orbit" aria-hidden="true"></div>
      <div class="taba-viz-header">
        <div>
          <p class="taba-viz-kicker">Interactive mental model</p>
          <h3 class="taba-viz-title">A finite sample from an infinite updateable table</h3>
          <p class="taba-viz-copy">
            Each row is a visible sampled region. The symbolic table is the rule behind the rows.
          </p>
        </div>
        <div class="taba-viz-formula" aria-label="Pointwise revision formula">
          Rev(i) = (G(i) meet A(i)) join (G(i)' meet T(i))
        </div>
      </div>

      <div class="taba-viz-controls" role="group" aria-label="Visualizer controls">
        <button class="taba-viz-button" type="button" data-action="step">Step revision</button>
        <button class="taba-viz-button" type="button" data-action="play">Play</button>
        <button class="taba-viz-button" type="button" data-action="split">Split selected region</button>
        <button class="taba-viz-button taba-viz-button-ghost" type="button" data-action="reset">Reset</button>
      </div>

      <div class="taba-viz-stage" aria-describedby="taba-viz-status-${index}">
        <div class="taba-viz-map" aria-label="Sampled Boolean regions"></div>
        <div class="taba-viz-table-wrap">
          <table class="taba-viz-table">
            <thead>
              <tr>
                <th scope="col">Sampled key and region</th>
                <th scope="col">Old T</th>
                <th scope="col">Guard G</th>
                <th scope="col">Replacement A</th>
                <th scope="col">Revised Rev</th>
              </tr>
            </thead>
            <tbody></tbody>
          </table>
        </div>
      </div>

      <div class="taba-viz-footer">
        <p class="taba-viz-status" id="taba-viz-status-${index}" aria-live="polite"></p>
        <div class="taba-viz-legend" aria-label="Legend">
          <span><i class="taba-viz-dot taba-viz-dot-guard"></i> inside fixed guard G</span>
          <span><i class="taba-viz-dot taba-viz-dot-outside"></i> outside G, so G' preserves T</span>
          <span><i class="taba-viz-dot taba-viz-dot-done"></i> revision has been applied</span>
        </div>
        <p class="taba-viz-scope">
          Scope note: this is a teaching model for safe pointwise revision. It is not a proof of
          atomlessness, full NSO, or unrestricted TABA tables.
        </p>
      </div>
    `;

    mount.replaceChildren(root);

    const map = root.querySelector(".taba-viz-map");
    const tbody = root.querySelector("tbody");
    const status = root.querySelector(".taba-viz-status");
    const playButton = root.querySelector('[data-action="play"]');
    const splitButton = root.querySelector('[data-action="split"]');

    function revisedValue(region, rowIndex) {
      if (rowIndex >= appliedCount) return "pending";
      return region.guard ? region.replacement : region.oldValue;
    }

    function statusText() {
      const selected = regions.find((region) => region.id === selectedId);
      if (!selected) return "Select a region to inspect the pointwise update.";
      if (appliedCount >= regions.length) {
        return "Revision complete. Inside G used A. Outside G used the old value T.";
      }
      return `Selected ${selected.key}, region ${selected.region}. Step revision applies Rev to the next sampled region. Split refines the selected nonzero region into two visible children.`;
    }

    function renderMap() {
      map.innerHTML = "";
      regions.forEach((region, rowIndex) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = [
          "taba-viz-region",
          region.guard ? "is-guard" : "is-outside",
          rowIndex < appliedCount ? "is-applied" : "",
          region.id === selectedId ? "is-selected" : "",
        ]
          .filter(Boolean)
          .join(" ");
        button.setAttribute("aria-pressed", region.id === selectedId ? "true" : "false");
        button.dataset.regionId = region.id;
        button.innerHTML = `
          <span class="taba-viz-region-key">${region.key}</span>
          <span class="taba-viz-region-name">${region.region}</span>
          <span class="taba-viz-region-rule">${region.guard ? "inside G" : "inside G'"}</span>
        `;
        button.addEventListener("click", () => {
          selectedId = region.id;
          render();
        });
        map.appendChild(button);
      });
    }

    function renderRows() {
      tbody.innerHTML = "";
      regions.forEach((region, rowIndex) => {
        const tr = document.createElement("tr");
        tr.className = region.id === selectedId ? "is-selected" : "";
        if (rowIndex < appliedCount) tr.classList.add("is-applied");

        const rev = revisedValue(region, rowIndex);
        tr.innerHTML = `
          <td>
            <button class="taba-viz-row-select" type="button" data-region-id="${region.id}" aria-pressed="${region.id === selectedId ? "true" : "false"}">
              <span>${region.key}</span>
              <strong>${region.region}</strong>
            </button>
          </td>
          <td><span class="taba-viz-pill taba-viz-pill-old">${region.oldValue}</span></td>
          <td><span class="taba-viz-pill ${region.guard ? "taba-viz-pill-guard" : "taba-viz-pill-outside"}">${region.guardText}</span></td>
          <td><span class="taba-viz-pill taba-viz-pill-replacement">${region.replacement}</span></td>
          <td><span class="taba-viz-pill ${rowIndex < appliedCount ? "taba-viz-pill-done" : "taba-viz-pill-pending"}">${rev}</span></td>
        `;

        tr.querySelector(".taba-viz-row-select").addEventListener("click", () => {
          selectedId = region.id;
          render();
        });
        tbody.appendChild(tr);
      });
    }

    function render() {
      renderMap();
      renderRows();
      status.textContent = statusText();
      playButton.textContent = playTimer ? "Pause" : "Play";
      splitButton.disabled = regions.length >= 10;
      splitButton.setAttribute("aria-disabled", regions.length >= 10 ? "true" : "false");
      splitButton.title =
        regions.length >= 10
          ? "The visualizer caps visible samples at ten rows."
          : "Split the selected nonzero region into two visible children.";
    }

    function stopPlay() {
      if (playTimer) {
        window.clearInterval(playTimer);
        playTimer = null;
      }
    }

    function stepRevision() {
      if (appliedCount < regions.length) {
        appliedCount += 1;
      } else {
        stopPlay();
      }
      render();
    }

    function splitSelectedRegion() {
      const selectedIndex = regions.findIndex((region) => region.id === selectedId);
      if (selectedIndex < 0 || regions.length >= 10) {
        status.textContent = "The visualizer caps visible samples at ten rows to stay readable.";
        return;
      }

      const selected = regions[selectedIndex];
      splitCounter += 1;
      const left = {
        ...selected,
        id: `${selected.id}-s${splitCounter}l`,
        region: `${selected.region}.0`,
      };
      const right = {
        ...selected,
        id: `${selected.id}-s${splitCounter}r`,
        region: `${selected.region}.1`,
      };

      regions.splice(selectedIndex, 1, left, right);
      selectedId = left.id;
      if (appliedCount > selectedIndex) {
        appliedCount = Math.min(regions.length, appliedCount + 1);
      }
      render();
      status.textContent =
        `Region ${selected.region} was split into ${left.region} and ${right.region}. This models the splitter idea: a nonzero region can have a proper nonzero subregion.`;
    }

    function togglePlay() {
      if (playTimer) {
        stopPlay();
        render();
        return;
      }

      playTimer = window.setInterval(() => {
        if (appliedCount >= regions.length) {
          stopPlay();
          render();
          return;
        }
        stepRevision();
      }, 900);
      render();
    }

    root.querySelector('[data-action="step"]').addEventListener("click", () => {
      stopPlay();
      stepRevision();
    });
    root.querySelector('[data-action="play"]').addEventListener("click", togglePlay);
    root.querySelector('[data-action="split"]').addEventListener("click", () => {
      stopPlay();
      splitSelectedRegion();
    });
    root.querySelector('[data-action="reset"]').addEventListener("click", () => {
      stopPlay();
      regions = cloneSeed();
      selectedId = regions[0].id;
      appliedCount = 0;
      splitCounter = 0;
      render();
    });

    render();
  }

  const boot = () => mounts.forEach(initVisualizer);

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }
})();
