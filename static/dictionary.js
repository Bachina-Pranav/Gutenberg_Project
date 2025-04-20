/*
 * Pop‑up dictionary: when the user selects a single word, fetch its definition
 * from https://api.dictionaryapi.dev and show it in a side panel.
 */
 const apiBase = "https://api.dictionaryapi.dev/api/v2/entries/en/";
 const panel   = document.getElementById("dict‑panel");
 const wordElt = document.getElementById("dict‑word");
 const defElt  = document.getElementById("dict‑definitions");
 const closeBtn= document.getElementById("dict‑close");
 
 function clearPanel() {
   wordElt.textContent = "";
   defElt.innerHTML = "";
 }
 
 closeBtn.addEventListener("click", () => {
   panel.hidden = true;
   clearPanel();
 });
 
 document.addEventListener("mouseup", () => {
   const selection = window.getSelection().toString().trim();
   if (!selection.match(/^[A-Za-z'-]+$/)) return; // only single words
 
   fetch(apiBase + encodeURIComponent(selection))
     .then(r => r.json())
     .then(json => {
       const defs = json[0]?.meanings || [];
       if (!defs.length) return;
 
       wordElt.textContent = selection;
       defElt.innerHTML = defs.map(m => `<p><em>${m.partOfSpeech}</em>: ${m.definitions[0].definition}</p>`).join("");
       panel.hidden = false;
       window.getSelection().removeAllRanges(); // now you don't need to click elsewhere to close the dictionary popup
     })
     .catch(console.error);
 });