<script>
    import { onMount } from 'svelte';
    
    // State variables
    let flightDate = new Date().toISOString().split('T')[0];
    let origin = 'MEX';
    let flightType = 'Nacional';
    let serviceType = 'Premium';
    let passengers = 180;
    
    let products = [
        {id: "P001", name: "Sandwich Jamón", proposedQty: 120},
        {id: "P002", name: "Ensalada César", proposedQty: 80},
        {id: "P003", name: "Pasta Alfredo", proposedQty: 100},
        {id: "P004", name: "Wrap Pollo", proposedQty: 90},
        {id: "P005", name: "Fruta Fresca", proposedQty: 150},
        {id: "P006", name: "Yogurt", proposedQty: 110},
        {id: "P007", name: "Galletas", proposedQty: 200},
        {id: "P008", name: "Café", proposedQty: 180},
        {id: "P009", name: "Jugo Naranja", proposedQty: 160},
        {id: "P010", name: "Agua", proposedQty: 250}
    ];
    
    let results = [];
    let showResults = false;
    let chartCanvas;
    let chart = null;
    
    // Opciones para los selectores
    const originOptions = ['MEX', 'CUN', 'GDL', 'MTY', 'TIJ'];
    const flightTypeOptions = ['Nacional', 'Internacional'];
    const serviceTypeOptions = ['Premium', 'Economico'];
    
    // Computed values
    $: totalProposed = results.reduce((sum, r) => sum + r.proposedQty, 0);
    $: totalOptimal = results.reduce((sum, r) => sum + r.optimal, 0);
    $: totalDiff = totalOptimal - totalProposed;
    
    // Función de predicción simulada
    function mockPredict(productData, flightParams) {
        const baseFactor = flightParams.passengers / 180;
        const typeFactor = flightParams.flightType === 'Internacional' ? 1.2 : 1.0;
        const serviceFactor = flightParams.serviceType === 'Premium' ? 1.3 : 1.0;
        
        return productData.map(p => {
            const randomVariation = 0.85 + Math.random() * 0.3;
            const optimal = Math.round(
                p.proposedQty * baseFactor * typeFactor * serviceFactor * randomVariation
            );
            return {
                ...p,
                optimal: optimal,
                diff: optimal - p.proposedQty
            };
        });
    }
    
    // Calcular carga óptima
    async function calculateOptimalLoad() {
          const response = await fetch('http://localhost:8000/api/predict', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
              products,
              flightDate,
              origin,
              flightType,
              serviceType,
              passengers
          })
      });
      results = await response.json();
      showResults = true;
      setTimeout(createChart, 100);
    }
    
    // Crear gráfico con Chart.js
    function createChart() {
        if (!chartCanvas) return;
        
        if (chart) {
            chart.destroy();
        }
        
        const ctx = chartCanvas.getContext('2d');
        chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: results.map(r => r.id),
                datasets: [
                    {
                        label: 'Proposed_Qty',
                        data: results.map(r => r.proposedQty),
                        backgroundColor: 'rgba(102, 126, 234, 0.7)',
                        borderColor: 'rgba(102, 126, 234, 1)',
                        borderWidth: 2
                    },
                    {
                        label: 'Optimal_Load_Pred',
                        data: results.map(r => r.optimal),
                        backgroundColor: 'rgba(118, 75, 162, 0.7)',
                        borderColor: 'rgba(118, 75, 162, 1)',
                        borderWidth: 2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    // Descargar CSV
    function downloadCSV() {
        const headers = ['Product_ID', 'Product_Name', 'Proposed_Qty', 'Optimal_Load_Pred', 'Diff_(Optimal-Prop)'];
        const rows = results.map(r => [
            r.id,
            r.name,
            r.proposedQty,
            r.optimal,
            r.diff
        ]);

        let csv = headers.join(',') + '\n';
        rows.forEach(row => {
            csv += row.join(',') + '\n';
        });

        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `optimal_load_${origin}_${flightType}_${serviceType}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
    }
    
    // Cargar Chart.js
    onMount(() => {
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js';
        document.head.appendChild(script);
    });
</script>

<div class="container">
    <h1>Optimal Food Load</h1>
    <p class="caption">RandomForest + Optuna (200 trials, CV estratificada por Product_ID).</p>

    <div class="form-grid">
        <div class="form-group">
            <label for="flightDate">Fecha del vuelo</label>
            <input type="date" id="flightDate" bind:value={flightDate}>
        </div>
        <div class="form-group">
            <label for="origin">Origin</label>
            <select id="origin" bind:value={origin}>
                {#each originOptions as opt}
                    <option value={opt}>{opt}</option>
                {/each}
            </select>
        </div>
        <div class="form-group">
            <label for="flightType">Flight Type</label>
            <select id="flightType" bind:value={flightType}>
                {#each flightTypeOptions as opt}
                    <option value={opt}>{opt}</option>
                {/each}
            </select>
        </div>
        <div class="form-group">
            <label for="serviceType">Service Type</label>
            <select id="serviceType" bind:value={serviceType}>
                {#each serviceTypeOptions as opt}
                    <option value={opt}>{opt}</option>
                {/each}
            </select>
        </div>
        <div class="form-group">
            <label for="passengers">Passenger Count</label>
            <input type="number" id="passengers" min="1" max="700" bind:value={passengers}>
        </div>
    </div>

    <div class="divider"></div>

    <h2>Cantidades propuestas por producto (edita libremente)</h2>
    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th>Product_ID</th>
                    <th>Product_Name</th>
                    <th>Proposed_Qty</th>
                </tr>
            </thead>
            <tbody>
                {#each products as product}
                    <tr>
                        <td>{product.id}</td>
                        <td>{product.name}</td>
                        <td>
                            <input 
                                type="number" 
                                bind:value={product.proposedQty} 
                                min="0" 
                                step="5"
                            >
                        </td>
                    </tr>
                {/each}
            </tbody>
        </table>
    </div>

    <button class="btn-primary" on:click={calculateOptimalLoad}>
        Calcular Carga Óptima
    </button>

    {#if showResults}
        <div class="results-section">
            <h2>Recomendación de carga óptima — TODOS los productos</h2>
            
            <div class="table-container">
                <table class="results-table">
                    <thead>
                        <tr>
                            <th>Product_ID</th>
                            <th>Product_Name</th>
                            <th>Proposed_Qty</th>
                            <th>Optimal_Load_Pred</th>
                            <th>Diff (Optimal-Prop)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each results as result}
                            <tr>
                                <td>{result.id}</td>
                                <td>{result.name}</td>
                                <td>{result.proposedQty}</td>
                                <td>{result.optimal}</td>
                                <td class={result.diff > 0 ? 'positive' : result.diff < 0 ? 'negative' : ''}>
                                    {result.diff > 0 ? '+' : ''}{result.diff}
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>

            <div class="chart-container">
                <canvas bind:this={chartCanvas}></canvas>
            </div>

            <div class="metrics">
                <div class="metric-card">
                    <div class="metric-label">Total propuesto</div>
                    <div class="metric-value">{totalProposed.toLocaleString()}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Total óptimo</div>
                    <div class="metric-value">{totalOptimal.toLocaleString()}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Óptimo - Propuesto</div>
                    <div class="metric-value">
                        {totalDiff > 0 ? '+' : ''}{totalDiff.toLocaleString()}
                    </div>
                </div>
            </div>

            <button class="btn-download" on:click={downloadCSV}>
                Descargar resultados (CSV)
            </button>
        </div>
    {/if}
</div>

<style>
    :global(body) {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        padding: 2rem;
        margin: 0;
    }

    .container {
        max-width: 1400px;
        margin: 0 auto;
        background: white;
        border-radius: 16px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        padding: 2rem;
    }

    h1 {
        color: #1a202c;
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }

    .caption {
        color: #718096;
        font-size: 0.9rem;
        margin-bottom: 2rem;
    }

    .form-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }

    .form-group {
        display: flex;
        flex-direction: column;
    }

    label {
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }

    input, select {
        padding: 0.75rem;
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        font-size: 1rem;
        transition: all 0.2s;
    }

    input:focus, select:focus {
        outline: none;
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }

    .divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        margin: 2rem 0;
    }

    h2 {
        color: #2d3748;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }

    .table-container {
        overflow-x: auto;
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        margin-bottom: 2rem;
    }

    table {
        width: 100%;
        border-collapse: collapse;
    }

    th {
        background: #f7fafc;
        padding: 1rem;
        text-align: left;
        font-weight: 600;
        color: #2d3748;
        border-bottom: 2px solid #e2e8f0;
    }

    td {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #e2e8f0;
    }

    td input {
        width: 100%;
        padding: 0.5rem;
    }

    tr:hover {
        background: #f7fafc;
    }

    .btn-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 2rem;
        border: none;
        border-radius: 8px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: transform 0.2s, box-shadow 0.2s;
        margin-bottom: 2rem;
    }

    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
    }

    .btn-primary:active {
        transform: translateY(0);
    }

    .metrics {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }

    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        margin-bottom: 0.5rem;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }

    .chart-container {
        margin: 2rem 0;
        padding: 1.5rem;
        background: #f7fafc;
        border-radius: 12px;
    }

    .btn-download {
        background: #48bb78;
        color: white;
        padding: 0.75rem 1.5rem;
        border: none;
        border-radius: 8px;
        font-size: 0.95rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
    }

    .btn-download:hover {
        background: #38a169;
        transform: translateY(-2px);
    }

    .results-table td.positive {
        color: #38a169;
        font-weight: 600;
    }

    .results-table td.negative {
        color: #e53e3e;
        font-weight: 600;
    }

    .results-section {
        animation: fadeIn 0.3s ease-in;
    }

    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
</style>