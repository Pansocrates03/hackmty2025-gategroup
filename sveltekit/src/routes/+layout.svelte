<script lang="ts">
        import '../app.css'
        let { data, children } = $props();
</script>

<div class="app-wrapper">
    {@render children()}
</div>

<style>
    .app-wrapper {
        max-width: 1100px;
        margin: 2rem auto;
        padding: 1rem;
    }
</style>