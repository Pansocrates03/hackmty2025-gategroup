<script lang="ts">
  export let data: { products: any[] };
</script>

<h1>Products</h1>

<!--
<section class="form-section">
  <h2>Añadir producto</h2>
  <form method="post">
    <div class="form-column">
      <label>
        Nombre
        <input name="name" required />
      </label>
      <label>
        Bar code
        <input name="bar_code" />
      </label>
      <label>
        Peso
        <input name="weight" type="number" step="any" />
      </label>
      <div class="form-actions">
        <button class="btn" type="submit">Añadir producto</button>
        <a class="link" href="/">Volver al dashboard</a>
      </div>
    </div>
  </form>
</section>
-->

<section>
  <h2>Products List</h2>
  {#if data?.products?.length}
    <table class="data-table">
      <thead>
        <tr><th>id</th><th>name</th><th>bar_code</th><th>weight</th></tr>
      </thead>
      <tbody>
        {#each data.products as p}
          <tr>
            <td>{p.id}</td>
            <td>{p.name}</td>
            <td>{p.barcode}</td>
            <td>{p.weight}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  {:else}
    <p class="muted">No hay productos.</p>
  {/if}
</section>

<style>
  :global(body) {
    font-family: 'Arial', sans-serif;
    background: #f9f9f9;
    color: #333;
    margin: 0;
    padding: 0;
  }

  h1 {
    font-size: 2rem;
    color: #444;
    text-align: center;
    margin-bottom: 1.5rem;
  }

  h2 {
    font-size: 1.5rem;
    color: #555;
    margin-bottom: 1rem;
  }

  .form-section {
    margin-bottom: 2rem;
    background: #ffffff;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }

  .form-column {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    max-width: 500px;
    margin: 0 auto;
  }

  label {
    display: flex;
    flex-direction: column;
    font-size: 0.9rem;
    color: #666;
  }

  input {
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 1rem;
    margin-top: 0.25rem;
  }

  .form-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
  }

  .btn {
    padding: 0.75rem 1.25rem;
    border-radius: 8px;
    background: #007BFF;
    color: white;
    border: none;
    cursor: pointer;
    font-size: 1rem;
    transition: background 0.3s;
  }

  .btn:hover {
    background: #0056b3;
  }

  .link {
    color: #007BFF;
    text-decoration: none;
    font-size: 0.9rem;
  }

  .link:hover {
    text-decoration: underline;
  }

  .data-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
    background: #fff;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .data-table th, .data-table td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid #eee;
  }

  .data-table th {
    background: #f4f4f4;
    font-weight: bold;
    color: #555;
  }

  .data-table tr:nth-child(even) {
    background: #f9f9f9;
  }

  .muted {
    color: #888;
    text-align: center;
    margin-top: 1rem;
  }
</style>
