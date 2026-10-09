import re

with open('index.html', 'r', encoding='utf-8') as f:
    data = f.read()

# Remove Load Preset button
data = re.sub(r'<button onclick="openModal\(\)".*?Load Preset.*?<\/button>', '', data, flags=re.DOTALL)

# Empty sources array
data = re.sub(r'let sources = \[.*?\];', 'let sources = [];', data, flags=re.DOTALL)

# Remove Modal HTML
data = re.sub(r'<!-- ═══ MODAL ═══ -->.*?<script>', '<script>', data, flags=re.DOTALL)

# Remove Modal JS functions
data = re.sub(r'function openModal\(\).*?function loadPreset\(scenario\) \{.*?\}\n', '', data, flags=re.DOTALL)
data = re.sub(r'async function loadPreset\(scenario\).*?\}\n', '', data, flags=re.DOTALL)

# Update texts
data = data.replace('Data Ingestion', 'Multi-Engine Pipeline')
data = data.replace('Cognitive Graph Fusion', 'Intent-Based Semantic API Gateway')
data = data.replace('Cognitive Graph', 'Semantic Gateway')
data = data.replace('Evidence Auditor', 'Autonomous Auditor')
data = data.replace('Action Synthesizer', 'Edge-to-Cloud Hybrid')
data = data.replace('Semantic Gateway — Evidence Comparison', 'Autonomous Drift & Conflict Resolver')
data = data.replace('Action Synthesizer Outputs', 'Edge-to-Cloud Hybrid Deployment')

# Remove MatchBadge
data = re.sub(r'<div id="matchBadge".*?</div>\s*</div>\s*<div class="grid grid-cols-12 gap-5">', '</div>\n                <div class="grid grid-cols-12 gap-5">', data, flags=re.DOTALL)

# Remove MatchBadge logic in renderAll
data = re.sub(r'// Dynamic Match Badge Calculation.*?// Sidebar Badge', '// Sidebar Badge', data, flags=re.DOTALL)

# Add Cloud Sync Permission to Tab 4
cloud_perm = """
                <div class="flex items-center justify-between p-4 bg-[#151822] border border-white/5 rounded-xl mb-6">
                    <div>
                        <h4 class="text-sm font-bold text-gray-200">Cloud Sync Permission (LLM Cluster)</h4>
                        <p class="text-[10px] text-gray-500">Authorize transmission of sanitized payloads to external Edge-to-Cloud Hybrid models.</p>
                    </div>
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" class="sr-only peer" checked>
                      <div class="w-11 h-6 bg-gray-700 rounded-full peer peer-checked:bg-blue-500 peer-checked:after:translate-x-full after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:rounded-full after:h-5 after:w-5 after:transition-all"></div>
                    </label>
                </div>
                <div id="actionCards"
"""
data = data.replace('<div id="actionCards"', cloud_perm)

# Change Execute to 'Push to Cloud'
data = data.replace('Execute\n                    </button>', 'Push to Cloud ☁️\n                    </button>')

# Improve graph node onClick
data = data.replace('return `<div class="graph-node" style="left:${p.x-22}px;top:${p.y-22}px;">',
                    'const alertText = `File: ${name}\\nEngine: ${engine}\\nSize: ${size}`; return `<div class="graph-node cursor-pointer group" style="left:${p.x-22}px;top:${p.y-22}px;" onclick="alert(alertText)">')
data = data.replace('return `<div class="graph-node cursor-pointer group" style="left:${p.x-22}px;top:${p.y-22}px;" title="File: ${name}&#10;Engine: ${engine}&#10;Size: ${size}">',
                    'const alertText = `File: ${name}\\nEngine: ${engine}\\nSize: ${size}`; return `<div class="graph-node cursor-pointer group" style="left:${p.x-22}px;top:${p.y-22}px;" onclick="alert(alertText)">')

# Add Bar graphs to Tab 2
bar_graph_html = """
                <div class="grid grid-cols-12 gap-5 h-full">
                    <div class="col-span-8 flex flex-col bg-[#0a0c13] border border-white/5 rounded-xl relative overflow-hidden" id="graphCanvas" style="min-height:420px;">
                        <div id="graphPlaceholder" class="absolute inset-0 flex flex-col items-center justify-center gap-3 text-gray-600">
                            <i data-lucide="network" class="w-10 h-10"></i>
                            <span class="text-sm">Run the pipeline to visualize the knowledge graph.</span>
                        </div>
                    </div>
                    
                    <div class="col-span-4 flex flex-col gap-4">
                        <div class="bg-[#151822] rounded-xl border border-white/5 p-5">
                            <h4 class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4 border-b border-white/5 pb-2">Data Modalities</h4>
                            <div class="space-y-3" id="barChart1">
                                <div class="text-[10px] text-gray-500 italic">Run pipeline to analyze distribution.</div>
                            </div>
                        </div>
                        <div class="bg-[#151822] rounded-xl border border-white/5 p-5 flex-1">
                            <h4 class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4 border-b border-white/5 pb-2">Risk Severity</h4>
                            <div class="space-y-3" id="barChart2">
                                <div class="text-[10px] text-gray-500 italic">No risks detected.</div>
                            </div>
                        </div>
                    </div>
                </div>
"""
data = re.sub(r'<div id="graphCanvas".*?</div>', bar_graph_html, data, flags=re.DOTALL)

# Add logic to populate bar charts
js_add = """
        // Populate Bar Charts
        const exts = sources.reduce((acc,s) => { acc[s.ext] = (acc[s.ext]||0)+1; return acc; }, {});
        const maxE = Math.max(...Object.values(exts), 1);
        document.getElementById('barChart1').innerHTML = Object.entries(exts).map(([k,v]) => `
            <div class="flex items-center gap-3 text-xs">
                <span class="w-8 font-mono text-gray-400">${k}</span>
                <div class="flex-1 bg-gray-800 rounded-full h-1.5"><div class="bg-blue-500 h-1.5 rounded-full" style="width:${(v/maxE)*100}%"></div></div>
                <span class="text-gray-300">${v}</span>
            </div>`).join('');
            
        const sevs = conflicts.reduce((acc,c) => { acc[c.severity] = (acc[c.severity]||0)+1; return acc; }, {CRITICAL:0, WARNING:0, INFO:0});
        const maxS = Math.max(...Object.values(sevs), 1);
        document.getElementById('barChart2').innerHTML = Object.entries(sevs).map(([k,v]) => {
            const c = k==='CRITICAL'?'red':(k==='WARNING'?'orange':'blue');
            return `
            <div class="flex items-center gap-3 text-xs">
                <span class="w-16 font-mono text-${c}-400">${k}</span>
                <div class="flex-1 bg-gray-800 rounded-full h-1.5"><div class="bg-${c}-500 h-1.5 rounded-full" style="width:${(v/maxS)*100}%"></div></div>
                <span class="text-gray-300">${v}</span>
            </div>`;
        }).join('');
"""
data = data.replace('canvas.innerHTML = `', js_add + '\\n        canvas.innerHTML = `')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(data)
