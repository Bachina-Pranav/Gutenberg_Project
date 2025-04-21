document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("btn-summary");
    if (!btn) return;
  
    btn.addEventListener("click", async () => {
      btn.disabled = true;
      btn.textContent = "Generating…";
  
      // derive slug from URL
      const parts = window.location.pathname.split("/");
      const slug  = parts[parts.length - 1];
  
      try {
        const res = await fetch(`/post/${slug}/summarize`, {
          method: "POST",
          headers: { "Content-Type": "application/json" }
        });
        const data = await res.json();
        document.getElementById("summary-container").innerHTML =
          `<h3>AI Summary</h3><p>${data.summary}</p>`;
      } catch (err) {
        console.error(err);
        alert("Sorry, summary failed.");
      } finally {
        btn.disabled = false;
        btn.textContent = "Generate summary";
      }
    });
  });
  