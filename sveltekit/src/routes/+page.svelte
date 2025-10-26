<script lang="ts">
  import { onMount } from 'svelte';
  export let data: { 
    products: any[]; 
    returned_products: any[];
    trolleys: any[];
  };

  let voiceText = '';
  let listening = false;
  let recognition: any = null;

  async function sendText() {
    if (!voiceText) return;
    try {
      const res = await fetch('/api/elevenlabs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: voiceText })
      });
      if (!res.ok) {
        const err = await res.text();
        alert('Error ElevenLabs: ' + err);
        return;
      }
      const buffer = await res.arrayBuffer();
      const blob = new Blob([buffer], { type: 'audio/mpeg' });
      const url = URL.createObjectURL(blob);
      const player: HTMLAudioElement | null = document.querySelector('#player');
      if (player) {
        player.src = url;
        player.hidden = false;
        player.play();
      }
    } catch (e) {
      console.error(e);
      alert('Error en la solicitud de voz');
    }
  }

  function startRecognition() {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('SpeechRecognition no es compatible en este navegador');
      return;
    }
    if (!recognition) {
      recognition = new SpeechRecognition();
      recognition.lang = 'es-MX';
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;
      recognition.onresult = (event: any) => {
        const text = event.results[0][0].transcript;
        voiceText = voiceText ? voiceText + ' ' + text : text;
      };
      recognition.onend = () => { listening = false; };
    }
    if (listening) {
      recognition.stop();
      listening = false;
    } else {
      recognition.start();
      listening = true;
    }
  }

  const navItems = [
    /*
    {
      href: '/realtime',
      title: 'Realtime Trolley Loading',
      description: 'Watch how the trolleys are getting loaded',
      icon: 'M3 7h18M5 11h14M7 15h10'
    },
    */
    {
      href: '/analysis',
      title: 'Optimal Load Prediction',
      description: 'Predict the amount of optimal food to load into the trolleys',
      icon: 'M3 3v18h18M7 13l3-3 3 4 4-6'
    },
    /*
    {
      href: '/optimization',
      title: 'Optimization',
      description: 'Improve returns',
      icon: 'M12 2v20M2 12h20'
    },
    */
    {
      href: '/productos',
      title: 'Resource Manager',
      description: 'Manage the inventory for your products',
      icon: 'M3 4h18v14H3z'
    }
  ];

  // Función para obtener el color según el estado
  function getStatusColor(status: string): string {
    const colors = {
      idle: '#94a3b8',      // gris
      loading: '#3b82f6',   // azul
      full: '#10b981',      // verde
      at_service: '#f59e0b' // naranja
    };
    return colors[status as keyof typeof colors] || '#6b7280';
  }

  // Función para obtener el texto del estado en español
  function getStatusText(status: string): string {
    const texts = {
      idle: 'Inactivo',
      loading: 'Cargando',
      full: 'Completo',
      at_service: 'En servicio'
    };
    return texts[status as keyof typeof texts] || status;
  }

  // Contar trolleys por estado
  $: trolleyStats = {
    idle: data?.trolleys?.filter(t => t.status === 'idle')?.length ?? 0,
    loading: data?.trolleys?.filter(t => t.status === 'loading')?.length ?? 0,
    full: data?.trolleys?.filter(t => t.status === 'full')?.length ?? 0,
    at_service: data?.trolleys?.filter(t => t.status === 'at_service')?.length ?? 0,
    total: data?.trolleys?.length ?? 0
  };

  // Formatear fecha
  function formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleString('es-MX', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
</script>

<!-- ElevenLabs voice agent UI -->
<section class="voice-agent">
  <h2>Agente de Voz</h2>
  <div class="voice-controls">
    <textarea id="voiceInput" placeholder="Escribe o presiona grabar y habla..." rows="3" bind:value={voiceText}></textarea>
    <div class="buttons">
      <button type="button" on:click={startRecognition}>{listening ? 'Detener' : 'Grabar'}</button>
      <button type="button" on:click={sendText} disabled={!voiceText}>Hablar</button>
    </div>
    <audio id="player" controls hidden></audio>
  </div>
</section>

<h1>Dashboard Admin</h1>

<!-- Sección de bienvenida -->
<section>
  <div class="grid-tiles">
    {#each navItems as item}
      <a class="tile" href={item.href}>
        <svg class="icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d={item.icon} stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <div class="tile-content">
          <div class="tile-title">{item.title}</div>
          <div class="tile-sub">{item.description}</div>
        </div>
      </a>
    {/each}
  </div>
</section>

<!-- Sección de estado de trolleys -->
<section class="trolleys-section">
  <h2>Estado de Trolleys en Tiempo Real</h2>
  
  <!-- Estadísticas rápidas -->
  <div class="stats-grid">
    <div class="stat-card">
      <div class="stat-value">{trolleyStats.total}</div>
      <div class="stat-label">Total Trolleys</div>
    </div>
    <div class="stat-card" style="--stat-color: {getStatusColor('idle')}">
      <div class="stat-value">{trolleyStats.idle}</div>
      <div class="stat-label">Inactivos</div>
    </div>
    <div class="stat-card" style="--stat-color: {getStatusColor('loading')}">
      <div class="stat-value">{trolleyStats.loading}</div>
      <div class="stat-label">Cargando</div>
    </div>
    <div class="stat-card" style="--stat-color: {getStatusColor('full')}">
      <div class="stat-value">{trolleyStats.full}</div>
      <div class="stat-label">Completos</div>
    </div>
    <div class="stat-card" style="--stat-color: {getStatusColor('at_service')}">
      <div class="stat-value">{trolleyStats.at_service}</div>
      <div class="stat-label">En Servicio</div>
    </div>
  </div>

  <!-- Lista de trolleys -->
  <div class="trolleys-list">
    {#each data.trolleys as trolley}
      <div class="trolley-card">
        <div class="trolley-header">
          <h3>{trolley.name}</h3>
          <span 
            class="status-badge" 
            style="background-color: {getStatusColor(trolley.status)}">
            {getStatusText(trolley.status)}
          </span>
        </div>
        <div class="trolley-footer">
          <span class="muted">Actualizado: {formatDate(trolley.updated_at)}</span>
        </div>
      </div>
    {/each}
  </div>

  {#if data.trolleys.length === 0}
    <div class="empty-state">
      <p class="muted">No hay trolleys registrados</p>
    </div>
  {/if}
</section>

<style>
  /* tiles grid */
  .grid-tiles { 
    display: grid; 
    grid-template-columns: repeat(2, 1fr); 
    gap: 1rem; 
    margin-top: 1rem;
    padding: 0.5rem;
  }

  .tile { 
    display: flex; 
    align-items: center; 
    gap: 0.75rem; 
    padding: 1rem; 
    border-radius: 8px; 
    background-color: #ffffff;
    text-decoration: none; 
    color: inherit; 
    border: 1px solid #e5e7eb;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  }

  /* Estilo de hover simplificado sin transformaciones ni transiciones */
  .tile:hover { 
    background-color: #f9fafb;
    border-color: #d1d5db;
  }

  .icon { 
    width: 40px; 
    height: 40px; 
    color: var(--color-theme-2); 
    flex: 0 0 40px; 
  }

  .tile-title { 
    font-weight: 600; 
    font-size: 1rem; 
  }

  .tile-sub { 
    font-size: 0.85rem; 
    color: rgba(0,0,0,0.6); 
  }

  /* general section/table styles */
  .muted { 
    color: rgba(0,0,0,0.55); 
  }
  
  section { 
    background: rgba(255,255,255,0.6); 
    padding: 0.75rem; 
    border-radius: 8px; 
    margin-bottom: 1rem; 
  }
  
  table.data-table { 
    width: 100%; 
    border-collapse: collapse; 
  }
  
  table.data-table th, table.data-table td { 
    padding: 0.5rem; 
    text-align: left; 
    border-bottom: 1px solid rgba(0,0,0,0.06); 
  }

  /* Trolleys section */
  .trolleys-section {
    margin-top: 1.5rem;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 0.75rem;
    margin: 1rem 0;
  }

  .stat-card {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    text-align: center;
    border: 2px solid rgba(0,0,0,0.06);
    transition: transform 0.2s ease;
  }

  .stat-card:hover {
    transform: translateY(-2px);
  }

  .stat-value {
    font-size: 2rem;
    font-weight: bold;
    color: var(--stat-color, var(--color-theme-2));
  }

  .stat-label {
    font-size: 0.85rem;
    color: rgba(0,0,0,0.6);
    margin-top: 0.25rem;
  }

  .trolleys-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 0.75rem;
    margin-top: 1rem;
  }

  .trolley-card {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid rgba(0,0,0,0.08);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }

  .trolley-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  }

  .trolley-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .trolley-header h3 {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 600;
  }

  .status-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    color: white;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .trolley-footer {
    font-size: 0.8rem;
  }

  .empty-state {
    text-align: center;
    padding: 2rem;
  }

  @media (max-width: 640px) {
    .grid-tiles { 
      grid-template-columns: repeat(2, 1fr); 
    }
    
    .icon { 
      width: 36px; 
      height: 36px; 
    }

    .stats-grid {
      grid-template-columns: repeat(2, 1fr);
    }

    .trolleys-list {
      grid-template-columns: 1fr;
    }
  }
</style>