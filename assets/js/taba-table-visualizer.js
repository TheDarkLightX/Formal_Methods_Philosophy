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
          <span class="taba-viz-formula-label">Pointwise revision</span>
          <span class="taba-viz-formula-body">Rev(i) = (G(i) ∧ A(i)) ∨ (G(i)′ ∧ T(i))</span>
        </div>
      </div>

      <div class="taba-viz-controls" role="group" aria-label="Visualizer controls">
        <button class="taba-viz-button" type="button" data-action="step" title="Apply revision to next region (Space)">
          <span class="taba-viz-button-icon" aria-hidden="true">▶</span>
          <span>Step revision</span>
        </button>
        <button class="taba-viz-button" type="button" data-action="play" title="Auto-advance every 0.9s (P)">
          <span class="taba-viz-button-icon" aria-hidden="true">⏵</span>
          <span class="taba-viz-button-label">Play</span>
        </button>
        <button class="taba-viz-button" type="button" data-action="split" title="Refine the selected region (S)">
          <span class="taba-viz-button-icon" aria-hidden="true">⇅</span>
          <span>Split selected region</span>
        </button>
        <button class="taba-viz-button taba-viz-button-ghost" type="button" data-action="reset" title="Restart (R)">
          <span class="taba-viz-button-icon" aria-hidden="true">↺</span>
          <span>Reset</span>
        </button>
        <div class="taba-viz-counter" aria-live="polite" aria-atomic="true">
          <span class="taba-viz-counter-num"><span data-counter-applied>0</span> / <span data-counter-total>4</span></span>
          <span class="taba-viz-counter-label">revisions applied</span>
        </div>
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
    const playLabel = playButton.querySelector(".taba-viz-button-label");
    const playIcon = playButton.querySelector(".taba-viz-button-icon");
    const splitButton = root.querySelector('[data-action="split"]');
    const counterApplied = root.querySelector("[data-counter-applied]");
    const counterTotal = root.querySelector("[data-counter-total]");

    function revisedValue(region, rowIndex) {
      if (rowIndex >= appliedCount) return "pending";
      return region.guard ? region.replacement : region.oldValue;
    }

    function statusText() {
      const selected = regions.find((region) => region.id === selectedId);
      if (!selected) return "Select a region to inspect the pointwise update.";
      if (appliedCount >= regions.length) {
        return "Revision complete. Inside G, each entry now shows A. Outside G, the old T was preserved.";
      }
      const remaining = regions.length - appliedCount;
      const next = regions[appliedCount];
      return `${remaining} ${remaining === 1 ? "region" : "regions"} pending. Next step revises ${next.key} (${next.region}) ${next.guard ? "inside G, so A wins" : "outside G, so T is kept"}.`;
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
      if (playLabel) playLabel.textContent = playTimer ? "Pause" : "Play";
      if (playIcon) playIcon.textContent = playTimer ? "⏸" : "⏵";
      counterApplied.textContent = String(appliedCount);
      counterTotal.textContent = String(regions.length);
      splitButton.disabled = regions.length >= 10;
      splitButton.setAttribute("aria-disabled", regions.length >= 10 ? "true" : "false");
      splitButton.title =
        regions.length >= 10
          ? "The visualizer caps visible samples at ten rows."
          : "Refine the selected region into two halves (S)";
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

    root.addEventListener("keydown", (event) => {
      if (event.target.closest("button, input, textarea, select")) return;
      if (event.metaKey || event.ctrlKey || event.altKey) return;
      const key = event.key.toLowerCase();
      if (key === " " || key === "enter") {
        event.preventDefault();
        stopPlay();
        stepRevision();
      } else if (key === "s") {
        event.preventDefault();
        stopPlay();
        splitSelectedRegion();
      } else if (key === "p") {
        event.preventDefault();
        togglePlay();
      } else if (key === "r") {
        event.preventDefault();
        stopPlay();
        regions = cloneSeed();
        selectedId = regions[0].id;
        appliedCount = 0;
        splitCounter = 0;
        render();
      }
    });
    root.setAttribute("tabindex", "0");

    render();
  }

  const boot = () => mounts.forEach(initVisualizer);

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }
})();
