/* ── JobGuard — Frontend Logic ──────────────────────────────────────────── */

const EXAMPLES = {
  real: `Software Engineer – ABC Tech Solutions

We are looking for a talented and motivated Software Engineer with 2+ years of experience in Python to join our growing engineering team. The ideal candidate will work on innovative products with a collaborative, fast-paced team.

Responsibilities:
- Design, develop and maintain scalable backend services using Python and Django
- Collaborate with frontend engineers, designers and product managers
- Write clean, well-tested and maintainable code
- Participate in code reviews and architectural discussions

Requirements:
- Bachelor's degree in Computer Science or equivalent
- 2+ years of professional Python development experience
- Experience with REST APIs, SQL databases, and Git
- Strong communication and problem-solving skills

Benefits:
- Competitive salary ($80,000 – $110,000 per year)
- Health, dental and vision insurance
- 20 days PTO, remote work options
- Annual learning and development budget

Apply via our careers portal at abctechsolutions.com/careers`,

  fake: `WORK FROM HOME!! Earn Rs 50,000 per week – No Experience Needed!!!

Amazing opportunity to earn HUGE income from the comfort of your home! No experience required. Immediate joining. No interview needed!

We are hiring for multiple positions. Part time / Full time available.

✅ Earn Rs 50,000 per week guaranteed
✅ Work just 2–3 hours daily
✅ No educational qualification required
✅ Get paid daily via online transfer

LIMITED SEATS AVAILABLE! Apply NOW before slots fill up!

For instant approval, contact us on WhatsApp: +91-XXXXXXXXXX
Send your name and location on WhatsApp now!!

Note: You must send a registration fee of Rs 500 to confirm your seat.`,
};

// ── DOM refs ──────────────────────────────────────────────────────────────────
const textarea     = document.getElementById("jobText");
const charCount    = document.getElementById("charCount");
const analyseBtn   = document.getElementById("analyseBtn");
const clearBtn     = document.getElementById("clearBtn");
const resultPanel  = document.getElementById("resultPanel");
const loadingEl    = document.getElementById("loading");
const resultBadge  = document.getElementById("resultBadge");
const resultLabel  = document.getElementById("resultLabel");
const riskLevel    = document.getElementById("riskLevel");
const realBar      = document.getElementById("realBar");
const fakeBar      = document.getElementById("fakeBar");
const realPct      = document.getElementById("realPct");
const fakePct      = document.getElementById("fakePct");
const flagsSection = document.getElementById("flagsSection");
const flagsList    = document.getElementById("flagsList");

// ── Character counter ─────────────────────────────────────────────────────────
textarea.addEventListener("input", () => {
  const len = textarea.value.length;
  charCount.textContent = `${len}/5000 characters`;
  charCount.style.color = len > 4500 ? "#ef4444" : "#9ca3af";
});

// ── Clear ──────────────────────────────────────────────────────────────────────
clearBtn.addEventListener("click", () => {
  textarea.value = "";
  charCount.textContent = "0/5000 characters";
  resultPanel.style.display = "none";
  loadingEl.style.display   = "none";
  analyseBtn.disabled = false;
});

// ── Try Example buttons ───────────────────────────────────────────────────────
document.querySelectorAll(".btn-try").forEach(btn => {
  btn.addEventListener("click", () => {
    const key = btn.dataset.example;
    textarea.value = EXAMPLES[key];
    charCount.textContent = `${EXAMPLES[key].length}/5000 characters`;
    resultPanel.style.display = "none";
    textarea.scrollIntoView({ behavior: "smooth", block: "center" });
    textarea.focus();
  });
});

// ── Analyse ────────────────────────────────────────────────────────────────────
analyseBtn.addEventListener("click", analysePosting);

async function analysePosting() {
  const text = textarea.value.trim();
  if (!text) {
    showError("Please enter a job description to analyse.");
    return;
  }
  if (text.length < 20) {
    showError("The text is too short. Please paste the full job description.");
    return;
  }

  resultPanel.style.display = "none";
  loadingEl.style.display   = "flex";
  analyseBtn.disabled = true;

  try {
    const response = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.error || "Server error");
    }

    const data = await response.json();
    renderResult(data);
  } catch (err) {
    showError(err.message || "Failed to connect to server. Make sure the backend is running.");
  } finally {
    loadingEl.style.display = "none";
    analyseBtn.disabled = false;
  }
}

// ── Render result ─────────────────────────────────────────────────────────────
function renderResult(data) {
  const isFake = data.label === "FAKE";

  resultPanel.className = "result-panel " + (isFake ? "result-fake" : "result-real");
  resultBadge.textContent = isFake ? "✕" : "✓";
  resultLabel.textContent = isFake
    ? "This posting appears to be FAKE"
    : "This posting appears to be REAL";
  riskLevel.textContent   = `Risk Level: ${data.risk_level}`;
  riskLevel.style.color   = isFake ? "#dc2626" : "#15803d";

  realBar.style.width = "0%";
  fakeBar.style.width = "0%";
  setTimeout(() => {
    realBar.style.width = data.real_prob + "%";
    fakeBar.style.width = data.fake_prob + "%";
  }, 80);

  realPct.textContent = data.real_prob + "%";
  fakePct.textContent = data.fake_prob + "%";

  if (data.flags && data.flags.length > 0) {
    flagsList.innerHTML = data.flags.map(f =>
      `<span class="flag-tag">${f}</span>`
    ).join("");
    flagsSection.style.display = "block";
  } else {
    flagsSection.style.display = "none";
  }

  resultPanel.style.display = "block";
  resultPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// ── Error display ─────────────────────────────────────────────────────────────
function showError(msg) {
  loadingEl.style.display   = "none";
  analyseBtn.disabled = false;
  resultPanel.className = "result-panel result-fake";
  resultBadge.textContent = "!";
  resultLabel.textContent = msg;
  riskLevel.textContent   = "";
  realBar.style.width = "0%";
  fakeBar.style.width = "0%";
  realPct.textContent = "";
  fakePct.textContent = "";
  flagsSection.style.display = "none";
  resultPanel.style.display  = "block";
}

// ── Load stats from API ────────────────────────────────────────────────────────
(async () => {
  try {
    const res   = await fetch("/api/stats");
    const stats = await res.json();
    document.getElementById("statAccuracy").textContent = stats.accuracy + "%";
    document.getElementById("statAuc").textContent      = stats.roc_auc  + "%";
    document.getElementById("statTotal").textContent    = stats.total_jobs.toLocaleString();
    document.getElementById("statFake").textContent     = stats.fake_jobs.toLocaleString();
  } catch (_) { /* use default values from HTML */ }
})();
