#!/usr/bin/env python3
"""Build docs/cba_availability_demos.html with embedded JSON. Run after docs/cba_demos_data.json exists."""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA_PATH = BASE / 'docs' / 'cba_demos_data.json'
OUT_PATH = BASE / 'docs' / 'cba_availability_demos.html'

def main():
    data = json.loads(DATA_PATH.read_text(encoding='utf-8'))
    json_str = json.dumps(data, separators=(',', ':'))
    # Prevent </script> in data from closing the script tag
    json_escaped = json_str.replace('</', r'<\/')

    html = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>CBA Availability — 3 Demos</title>
  <style>
    * { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; margin: 1rem; background: #1a1a1a; color: #e0e0e0; max-width: 1200px; }
    h1 { font-size: 1.35rem; margin-bottom: 0.25rem; }
    .tabs { display: flex; gap: 0.5rem; margin: 1rem 0; flex-wrap: wrap; }
    .tabs button { padding: 0.5rem 1rem; background: #333; color: #ccc; border: 1px solid #444; border-radius: 6px; cursor: pointer; }
    .tabs button:hover { background: #404040; color: #fff; }
    .tabs button.active { background: #2d4a2d; color: #b8f0b8; border-color: #3d6a3d; }
    .panel { display: none; padding: 1rem; background: #252525; border-radius: 8px; border: 1px solid #333; }
    .panel.active { display: block; }
    .panel h2 { font-size: 1rem; margin-top: 0; margin-bottom: 0.75rem; color: #9ee09e; }
    label { display: block; margin-top: 0.75rem; font-size: 0.9rem; }
    select, input[type="number"] { margin-left: 0.5rem; padding: 0.35rem; background: #333; color: #e0e0e0; border: 1px solid #444; border-radius: 4px; }
    .result { margin-top: 1rem; padding: 1rem; background: #1e1e1e; border-radius: 6px; font-size: 0.9rem; }
    .result ul { margin: 0.5rem 0 0 1rem; padding: 0; }
    .result li { margin: 0.25rem 0; }
    .slot-list { list-style: none; margin: 0; padding: 0; }
    .slot-list li { padding: 0.5rem; margin: 0.5rem 0; background: #2a2a2a; border-radius: 4px; border-left: 3px solid #3d6a3d; }
    .filter-row { display: flex; flex-wrap: wrap; gap: 1rem; align-items: center; margin-bottom: 1rem; }
    .filter-row label { margin-top: 0; display: inline-flex; align-items: center; }
    table { border-collapse: collapse; font-size: 0.7rem; }
    th, td { border: 1px solid #333; padding: 0.2rem 0.35rem; text-align: center; min-width: 3rem; }
    th { background: #2a2a2a; }
    th.row-header { text-align: right; padding-right: 0.5rem; }
    td.cell-0 { background: #2d2d2d; color: #666; }
    td.cell-1 { background: #3d3d2a; color: #b8b84e; }
    td.cell-2 { background: #2a3d2a; color: #7cb87c; }
    td.cell-3 { background: #1e3d1e; color: #9ee09e; }
    td.cell-4 { background: #0e4d0e; color: #b8f0b8; }
    td.cell-hide { display: none; }
    td.clickable { cursor: pointer; }
    td.clickable:hover { outline: 2px solid #6a9a6a; }
    .popover { position: fixed; background: #2a2a2a; border: 1px solid #444; border-radius: 6px; padding: 0.75rem; max-width: 360px; max-height: 70vh; overflow-y: auto; z-index: 10; font-size: 0.8rem; }
    .popover h4 { margin: 0 0 0.5rem 0; font-size: 0.85rem; }
    .popover ul { margin: 0; padding-left: 1.2rem; }
    .funding-panel { margin: 0 0 1.25rem; padding: 1rem 1.1rem; background: #252525; border: 1px solid #444; border-left: 4px solid #b8b84e; border-radius: 8px; }
    .funding-panel h2 { font-size: 1rem; margin: 0 0 0.5rem; color: #e8d87a; }
    .funding-panel p, .funding-panel li { font-size: 0.9rem; color: #d0d0d0; }
    .funding-panel .warn { color: #f0c674; font-weight: 600; }
    .funding-table { width: 100%; border-collapse: collapse; margin: 0.75rem 0; font-size: 0.85rem; }
    .funding-table th, .funding-table td { border: 1px solid #444; padding: 0.45rem 0.55rem; text-align: left; }
    .funding-table th { background: #2f2f2f; color: #e0e0e0; }
    .funding-table td.num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
    .funding-table tr.total td { font-weight: 600; color: #b8f0b8; }
  </style>
</head>
<body>
  <h1>A Study in Decision Making — team scheduling</h1>
  <p style="color:#888; font-size:0.9rem;">Spring 2026: faculty office hours × Powell/White room availability (20+ seats). Use the demos below to line up pilot and main-study sessions.</p>

  <section class="funding-panel" id="cash-plan">
    <h2>Cash float plan (main study only — do not count on Research Council)</h2>
    <p class="warn">We applied to the Nicholls State University Research Council, but that award is <strong>not guaranteed</strong>. Budget and staffing below assume <strong>no grant money</strong>. If an award is granted later, we will reconcile it against documented out-of-pocket costs; do not spend it until confirmed.</p>
    <p><strong>Pilot sessions:</strong> no participant cash compensation — investigators contribute <strong>$0</strong> in participant payments for pilot.</p>
    <p><strong>Main study:</strong> each participant receives a <strong>$14.00</strong> envelope at the start of the session (self-payment; they keep at least <strong>$10.00</strong>, up to <strong>$14.00</strong> depending on condition). Unearned bills are returned anonymously in-session. Protocol target: ~<strong>200</strong> main-study participants; up to <strong>20</strong> per session.</p>

    <table class="funding-table">
      <thead>
        <tr><th>Investigator</th><th>Upfront share (start of main data collection)</th><th>Expected return after main data collection ends</th><th>Expected net cost (no grant)</th></tr>
      </thead>
      <tbody>
        <tr><td>Dr. Christopher Castille (PI)</td><td class="num">$560</td><td class="num">~$160</td><td class="num">~$400</td></tr>
        <tr><td>Dr. Ann-Marie R. Castille</td><td class="num">$560</td><td class="num">~$160</td><td class="num">~$400</td></tr>
        <tr><td>Dr. Samantha Falgout</td><td class="num">$560</td><td class="num">~$160</td><td class="num">~$400</td></tr>
        <tr><td>Dr. Kaitlin Gravois</td><td class="num">$560</td><td class="num">~$160</td><td class="num">~$400</td></tr>
        <tr><td>Dr. Adrien Maught</td><td class="num">$560</td><td class="num">~$160</td><td class="num">~$400</td></tr>
        <tr class="total"><td>Team total (5 investigators, equal split)</td><td class="num">$2,800</td><td class="num">~$800</td><td class="num">~$2,000</td></tr>
      </tbody>
    </table>

    <p><strong>How the numbers work</strong></p>
    <ul>
      <li><strong>Upfront:</strong> $2,800 total float = 200 participants × $14 envelope. Split five ways → <strong>$560 per investigator</strong> contributed to the shared cash pool when we begin main data collection together.</li>
      <li><strong>Per full session (20 participants):</strong> whoever runs the room needs <strong>$280</strong> in mixed bills on hand ($14 × 20), drawn from the pool or replenished after reconciliation.</li>
      <li><strong>After main data collection ends:</strong> participants keep about <strong>$10 on average</strong> (~$2,000 paid out). Roughly <strong>$800</strong> in unearned cash should return to the team pool → about <strong>$160 per investigator</strong> if we split returns equally.</li>
      <li><strong>Net without grant:</strong> about <strong>$400 per investigator</strong> out of pocket ($560 in − ~$160 back). Actual returns vary slightly by condition mix (reward-goal participants average ~$10 but may keep up to $14).</li>
    </ul>
    <p style="color:#888; font-size:0.82rem; margin-bottom:0;">Assumptions match Appendix B2 / main-study consent and HSIRB packet payment language. Pilot uses Appendix B only (no cash). Research Council funding, if awarded, is applied after the fact—not built into these figures.</p>
  </section>

  <h2 style="font-size:1.05rem; margin:1rem 0 0.5rem; color:#9ee09e;">Scheduling demos</h2>
  <div class="tabs" role="tablist">
    <button type="button" class="active" data-panel="time-first" role="tab">1. Time-first</button>
    <button type="button" data-panel="slot-finder" role="tab">2. Study-slot finder</button>
    <button type="button" data-panel="heatmap" role="tab">3. Filterable heatmap</button>
  </div>

  <div id="time-first" class="panel active" role="tabpanel">
    <h2>Pick a slot → see who is available and which rooms are free</h2>
    <label>Day <select id="tf-day"></select></label>
    <label>Time (30-min slot) <select id="tf-time"></select></label>
    <div id="tf-result" class="result"></div>
  </div>

  <div id="slot-finder" class="panel" role="tabpanel">
    <h2>Find best 1-hour slots matching your criteria</h2>
    <div class="filter-row">
      <label>Min faculty in office <input type="number" id="sf-min-faculty" min="1" max="4" value="1"></label>
      <label>Min room capacity (e.g. 20 or 40) <input type="number" id="sf-min-cap" min="20" value="20" step="5"></label>
      <button type="button" id="sf-go">Find slots</button>
    </div>
    <div id="sf-result" class="result"></div>
  </div>

  <div id="heatmap" class="panel" role="tabpanel">
    <h2>Heatmap: filter by faculty and room size, click a cell for room list</h2>
    <div class="filter-row">
      <label><input type="checkbox" id="hm-f-maught"> Dr. Maught</label>
      <label><input type="checkbox" id="hm-f-castille"> Ann-Marie Castille</label>
      <label><input type="checkbox" id="hm-f-falgout"> Dr. Falgout</label>
      <label><input type="checkbox" id="hm-f-gravois"> Dr. Gravois</label>
      <label>At least one room with capacity ≥ <select id="hm-min-cap"><option value="0">any</option><option value="20">20</option><option value="40" selected>40</option></select></label>
      <button type="button" id="hm-update">Update heatmap</button>
    </div>
    <div id="heatmap-table-wrap"></div>
    <div id="hm-popover" class="popover" style="display:none;"></div>
  </div>

  <script type="application/json" id="cba-demos-data">''' + json_escaped + '''</script>
  <script>
(function() {
  var data = JSON.parse(document.getElementById('cba-demos-data').textContent);
  var dayNames = data.dayNames;
  var slotLabels = data.slotLabels;
  var grid = data.grid;
  var candidates = data.candidates;

  // Tabs
  document.querySelectorAll('.tabs button').forEach(function(btn) {
    btn.addEventListener('click', function() {
      document.querySelectorAll('.tabs button').forEach(function(b) { b.classList.remove('active'); });
      document.querySelectorAll('.panel').forEach(function(p) { p.classList.remove('active'); });
      btn.classList.add('active');
      document.getElementById(btn.getAttribute('data-panel')).classList.add('active');
    });
  });

  // Demo 1: Time-first
  var tfDay = document.getElementById('tf-day');
  var tfTime = document.getElementById('tf-time');
  var tfResult = document.getElementById('tf-result');
  dayNames.forEach(function(name, i) {
    var opt = document.createElement('option');
    opt.value = i;
    opt.textContent = name;
    tfDay.appendChild(opt);
  });
  slotLabels.forEach(function(label, i) {
    var opt = document.createElement('option');
    opt.value = i;
    opt.textContent = label;
    tfTime.appendChild(opt);
  });
  function updateTimeFirst() {
    var day = parseInt(tfDay.value, 10);
    var slotIdx = parseInt(tfTime.value, 10);
    var cell = grid[day][slotIdx];
    var f = cell.faculty;
    var rooms = cell.rooms;
    if (f.length === 0 && rooms.length === 0) {
      tfResult.innerHTML = '<p>No faculty in office and no free rooms in this slot.</p>';
      return;
    }
    var html = '';
    if (f.length > 0) {
      html += '<p><strong>Faculty in office:</strong></p><ul><li>' + f.join('</li><li>') + '</li></ul>';
    } else {
      html += '<p><strong>Faculty in office:</strong> None.</p>';
    }
    if (rooms.length > 0) {
      html += '<p><strong>Available rooms (' + rooms.length + '):</strong></p><ul>';
      rooms.forEach(function(r) {
        html += '<li>' + r.room + ' (cap ' + r.capacity + ')</li>';
      });
      html += '</ul>';
    } else {
      html += '<p><strong>Available rooms:</strong> None.</p>';
    }
    tfResult.innerHTML = html;
  }
  tfDay.addEventListener('change', updateTimeFirst);
  tfTime.addEventListener('change', updateTimeFirst);
  updateTimeFirst();

  // Demo 2: Study-slot finder
  document.getElementById('sf-go').addEventListener('click', function() {
    var minF = parseInt(document.getElementById('sf-min-faculty').value, 10) || 1;
    var minCap = parseInt(document.getElementById('sf-min-cap').value, 10) || 20;
    var filtered = candidates.filter(function(c) {
      return c.faculty.length >= minF && c.maxCapacity >= minCap;
    });
    filtered.sort(function(a, b) {
      if (b.faculty.length !== a.faculty.length) return b.faculty.length - a.faculty.length;
      return b.roomCount - a.roomCount;
    });
    var html = '<p><strong>' + filtered.length + ' slot(s) match.</strong></p><ul class="slot-list">';
    filtered.forEach(function(c) {
      html += '<li><strong>' + c.dayName + ' ' + c.startLabel + '–' + c.endLabel + '</strong><br>Faculty: ' + c.faculty.join(', ') + '. Rooms (' + c.roomCount + '): ' + c.rooms.map(function(r) { return r.room + ' (' + r.capacity + ')'; }).join(', ') + '.</li>';
    });
    html += '</ul>';
    document.getElementById('sf-result').innerHTML = html;
  });

  // Demo 3: Filterable heatmap
  var hmPopover = document.getElementById('hm-popover');
  function buildHeatmap() {
    var needMaught = document.getElementById('hm-f-maught').checked;
    var needCastille = document.getElementById('hm-f-castille').checked;
    var needFalgout = document.getElementById('hm-f-falgout').checked;
    var needGravois = document.getElementById('hm-f-gravois').checked;
    var minCap = parseInt(document.getElementById('hm-min-cap').value, 10) || 0;
    var anyFilter = needMaught || needCastille || needFalgout || needGravois;

    var wrap = document.getElementById('heatmap-table-wrap');
    var tbl = document.createElement('table');
    var thead = '<thead><tr><th class="row-header">Time</th><th>Mon</th><th>Tue</th><th>Wed</th><th>Thu</th><th>Fri</th></tr></thead><tbody>';
    var tbody = '';
    for (var si = 0; si < slotLabels.length; si++) {
      tbody += '<tr><th class="row-header">' + slotLabels[si] + '</th>';
      for (var day = 0; day < 5; day++) {
        var cell = grid[day][si];
        var f = cell.faculty;
        var rooms = cell.rooms;
        var hasBig = minCap === 0 || rooms.some(function(r) { return r.capacity >= minCap; });
        var pass = hasBig && (!anyFilter || (needMaught && f.indexOf('Dr. Maught') >= 0) || (needCastille && f.indexOf('Ann-Marie Castille') >= 0) || (needFalgout && f.indexOf('Dr. Samantha Falgout') >= 0) || (needGravois && f.indexOf('Dr. Gravois') >= 0));
        var cls = 'cell-' + f.length;
        if (!pass) cls += ' cell-hide';
        var title = dayNames[day] + ' ' + slotLabels[si] + ': ' + f.length + ' faculty, ' + rooms.length + ' rooms. Click for list.';
        var label = f.length + 'F ' + rooms.length + 'R';
        tbody += '<td class="' + cls + ' clickable" data-day="' + day + '" data-slot="' + si + '" title="' + title.replace(/"/g, '&quot;') + '">' + label + '</td>';
      }
      tbody += '</tr>';
    }
    tbl.innerHTML = thead + tbody + '</tbody>';
    tbl.querySelectorAll('td.clickable').forEach(function(td) {
      td.addEventListener('click', function() {
        var day = parseInt(this.getAttribute('data-day'), 10);
        var slot = parseInt(this.getAttribute('data-slot'), 10);
        var cell = grid[day][slot];
        hmPopover.innerHTML = '<h4>' + dayNames[day] + ' ' + slotLabels[slot] + '</h4><p><strong>Faculty:</strong> ' + (cell.faculty.length ? cell.faculty.join(', ') : 'None') + '</p><p><strong>Rooms:</strong></p><ul>' + cell.rooms.map(function(r) { return '<li>' + r.room + ' (' + r.capacity + ')</li>'; }).join('') + '</ul>';
        hmPopover.style.display = 'block';
        hmPopover.style.left = (this.getBoundingClientRect().left + window.scrollX) + 'px';
        hmPopover.style.top = (this.getBoundingClientRect().bottom + 4 + window.scrollY) + 'px';
      });
    });
    wrap.innerHTML = '';
    wrap.appendChild(tbl);
    document.addEventListener('click', function(e) {
      if (!hmPopover.contains(e.target) && !e.target.classList.contains('clickable')) hmPopover.style.display = 'none';
    });
  }
  document.getElementById('hm-update').addEventListener('click', buildHeatmap);
  buildHeatmap();
})();
  </script>
</body>
</html>
'''
    OUT_PATH.write_text(html, encoding='utf-8')
    print('Wrote', OUT_PATH)

if __name__ == '__main__':
    main()
