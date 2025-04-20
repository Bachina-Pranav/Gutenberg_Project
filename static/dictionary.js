/*
 * Single‑word  = look‑up in the side dictionary.
 * Multi‑word    = toggle highlight (add/remove <mark class="user-highlight">).
 */
const apiBase = "https://api.dictionaryapi.dev/api/v2/entries/en/";

// ----- dictionary panel -----------------------------
const panel    = document.getElementById("dict‑panel");
const wordElt  = document.getElementById("dict‑word");
const defElt   = document.getElementById("dict‑definitions");
const closeBtn = document.getElementById("dict‑close");

closeBtn.addEventListener("click", () => {
  panel.hidden = true;
  wordElt.textContent = "";
  defElt.innerHTML = "";
});

// ----------------------------------------------------
//  highlight helpers
function wrapRange(range) {
  const mark = document.createElement("mark");
  mark.className = "user-highlight";
  range.surroundContents(mark);
}
function unwrap(node) {
  const parent = node.parentNode;
  while (node.firstChild) parent.insertBefore(node.firstChild, node);
  parent.removeChild(node);
}

// ----------------------------------------------------
//  main handler
document.addEventListener("mouseup", () => {
  const sel = window.getSelection();
  const text = sel.toString().trim();

  // nothing selected
  if (!text) return;

  // if selection is *inside* an existing highlight => remove it
  const anchorHighlight = sel.anchorNode.parentElement.closest(".user-highlight");
  if (anchorHighlight) {
    unwrap(anchorHighlight);
    sel.removeAllRanges();
    return;
  }

  // single word => dictionary
  if (/^[A-Za-z'-]+$/.test(text)) {
    fetch(apiBase + encodeURIComponent(text))
      .then(r => r.json())
      .then(json => {
        const defs = json[0]?.meanings || [];
        if (!defs.length) return;

        wordElt.textContent = text;
        defElt.innerHTML =
          defs.map(m => `<p><em>${m.partOfSpeech}</em>: ${m.definitions[0].definition}</p>`).join("");
        panel.hidden = false;
        sel.removeAllRanges();
      })
      .catch(console.error);
    return;
  }

  // multi‑word => add highlight
  const range = sel.getRangeAt(0);
  // avoid trying to highlight across block boundaries (quick‑n‑dirty guard)
  // if (range.startContainer !== range.endContainer) {
  //   sel.removeAllRanges();
  //   return;
  // }
  wrapRange(range);
  sel.removeAllRanges();
});
