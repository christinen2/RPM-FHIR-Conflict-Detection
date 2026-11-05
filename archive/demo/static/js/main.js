document.addEventListener("DOMContentLoaded", () => {
  const scenariosDataElement = document.getElementById("scenariosData");
  const scenarios = JSON.parse(scenariosDataElement.textContent);

  const scenarioSelect = document.getElementById("scenarioSelect");
  const jsonViewer = document.getElementById("jsonViewer");
  const resultsContainer = document.getElementById("resultsContainer");
  const runBtn = document.getElementById("runBtn");
  const scenarioImage = document.getElementById("scenarioImage"); // Added image element reference

  function loadScenario() {
    const selectedKey = scenarioSelect.value;

    jsonViewer.value = JSON.stringify(scenarios[selectedKey].json, null, 2);

    resultsContainer.innerHTML =
      '<p class="text-sm text-slate-400">Ready to run conflict detection...</p>';

    if (scenarioImage) {
      scenarioImage.src = `/static/images/${selectedKey}.png`;
    }
  }

  async function runPipeline() {
    const selectedKey = scenarioSelect.value;
    const payload = scenarios[selectedKey].json;

    // Show loading state
    resultsContainer.innerHTML = `
            <div class="text-center text-indigo-600 animate-pulse">
                <p class="text-sm font-medium">Executing conflict detection engine...</p>
            </div>`;

    try {
      const res = await fetch("/api/detect-conflicts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      const report = data.conflicts;

      resultsContainer.innerHTML = "";

      if (!report || report.length === 0) {
        resultsContainer.innerHTML = `
                    <div class="w-full bg-emerald-50 border border-emerald-200 rounded-lg p-5 text-center shadow-sm">
                        <div class="text-emerald-700 text-2xl font-bold mb-1">✓ NO CONFLICTS</div>
                        <p class="text-xs text-emerald-600">The CarePlan target thresholds are compatible and within safety guidelines.</p>
                    </div>`;
        return;
      }

      if (Array.isArray(report)) {
        console.log(report);
        report.forEach((item, index) => {
          const contentHtml =
            typeof item === "object"
              ? `<pre class="text-xs font-mono text-rose-900 bg-rose-100/60 p-3 rounded border border-rose-200/60 whitespace-pre-wrap overflow-x-auto">${JSON.stringify(item, null, 2)}</pre>`
              : `<p class="text-xs text-rose-900 font-medium">${item}</p>`;

          resultsContainer.innerHTML += `
                        <div class="w-full bg-rose-50 border border-rose-200 rounded-lg p-4 mb-3 shadow-sm">
                            <div class="flex items-center justify-between mb-2">
                                <span class="bg-rose-100 text-rose-800 text-[10px] font-bold px-2 py-0.5 rounded uppercase border border-rose-200">Conflict #${index + 1}</span>
                            </div>
                            ${contentHtml}
                        </div>`;
        });
      } else {
        resultsContainer.innerHTML = `
                    <div class="w-full bg-rose-50 border border-rose-200 rounded-lg p-4 shadow-sm">
                        <pre class="text-xs font-mono text-rose-900 bg-rose-100/60 p-3 rounded border border-rose-200/60 whitespace-pre-wrap overflow-x-auto">${typeof report === "object" ? JSON.stringify(report, null, 2) : report}</pre>
                    </div>`;
      }
    } catch (err) {
      resultsContainer.innerHTML = `<p class="text-sm text-rose-600">Error connecting to detection engine server.</p>`;
      console.error(err);
    }
  }

  scenarioSelect.addEventListener("change", loadScenario);
  runBtn.addEventListener("click", runPipeline);

  loadScenario();
});
