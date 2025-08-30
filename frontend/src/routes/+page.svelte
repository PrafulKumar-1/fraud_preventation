<script lang="ts">
  import SearchBar from '$lib/components/SearchBar.svelte';
  import Uploader from '$lib/components/Uploader.svelte';
  let activeTab: 'advisor' | 'media' | 'document' = 'advisor';
</script>

<main class="container mx-auto p-4 md:p-8 max-w-4xl">
  <header class="text-center mb-8">
    <h1 class="text-4xl font-bold text-gray-800">Project Suraksha</h1>
    <p class="text-lg text-gray-600 mt-2">Verify, Then Trust. Your AI-Powered Investor Protection Toolkit.</p>
  </header>

  <div class="tabs mb-6 flex justify-center border-b">
    <button
      class="px-4 py-2 -mb-px font-semibold border-b-2"
      class:border-blue-500={activeTab === 'advisor'}
      class:text-blue-600={activeTab === 'advisor'}
      class:border-transparent={activeTab!== 'advisor'}
      on:click={() => activeTab = 'advisor'}
    >
      Verify Advisor
    </button>
    <button
      class="px-4 py-2 -mb-px font-semibold border-b-2"
      class:border-blue-500={activeTab === 'media'}
      class:text-blue-600={activeTab === 'media'}
      class:border-transparent={activeTab!== 'media'}
      on:click={() => activeTab = 'media'}
    >
      Scan Media
    </button>
    <button
      class="px-4 py-2 -mb-px font-semibold border-b-2"
      class:border-blue-500={activeTab === 'document'}
      class:text-blue-600={activeTab === 'document'}
      class:border-transparent={activeTab!== 'document'}
      on:click={() => activeTab = 'document'}
    >
      Check Document
    </button>
  </div>

  <div class="bg-white p-6 rounded-lg shadow-md">
    {#if activeTab === 'advisor'}
      <SearchBar />
    {:else if activeTab === 'media'}
      <Uploader
        title="Media Authenticity Scanner"
        description="Upload a video or audio file to check for signs of AI manipulation (deepfakes)."
        endpoint="/api/v1/scan/media"
        acceptedFileTypes="video/*,audio/*"
      />
    {:else if activeTab === 'document'}
      <Uploader
        title="Document Integrity Check"
        description="Upload a PDF or image file to check for signs of tampering or forgery."
        endpoint="/api/v1/scan/document"
        acceptedFileTypes="application/pdf,image/*"
      />
    {/if}
  </div>
</main>

<style>
  /* Basic TailwindCSS utility classes are assumed to be available */
  /* In a real project, you would set up TailwindCSS with SvelteKit */
</style>