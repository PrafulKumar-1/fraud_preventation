<script lang="ts">
  let query = '';
  let results: any[] = [];
  let status = 'idle'; // idle, loading, success, error, notfound
  let errorMessage = '';
  let debounceTimer: number;

  const handleInput = () => {
    clearTimeout(debounceTimer);
    if (query.length < 3) {
      status = 'idle';
      results = [];
      return;
    }
    status = 'loading';
    debounceTimer = window.setTimeout(() => {
      searchAdvisors();
    }, 500); // 500ms debounce
  };

  const searchAdvisors = async () => {
    // IMPORTANT: Replace with your actual backend URL when deployed
    const backendUrl = 'http://127.0.0.1:8000'; // For local dev
    // const backendUrl = 'https://your-render-app-name.onrender.com'; // For production
    try {
      const response = await fetch(`${backendUrl}/api/v1/verify/intermediary?query=${encodeURIComponent(query)}`);
      if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
      }
      const data = await response.json();
      if (data.status === 'Verified') {
        results = data.results;
        status = 'success';
      } else {
        results =[];
        status = 'notfound';
      }
    } catch (err) {
      status = 'error';
      errorMessage = err instanceof Error? err.message : 'An unknown error occurred.';
      results =[];
    }
  };
</script>

<div>
  <h2 class="text-2xl font-semibold mb-4 text-gray-700">Advisor & Intermediary Verification</h2>
  <input
    type="search"
    bind:value={query}
    on:input={handleInput}
    placeholder="Enter Advisor Name or Registration Number..."
    class="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
  />

  <div class="mt-6">
    {#if status === 'loading'}
      <p class="text-center text-gray-500">Searching...</p>
    {:else if status === 'success'}
      <div class="space-y-4">
        {#each results as result}
          <div class="p-4 border rounded-md bg-green-50 border-green-200">
            <p class="font-bold text-lg text-green-800">{result.name}</p>
            <p class="text-sm text-gray-600"><strong>Reg. No:</strong> {result.registration_no}</p>
            <p class="text-sm text-gray-600"><strong>Address:</strong> {result.address}</p>
            <p class="text-sm text-gray-600"><strong>Type:</strong> {result.entity_type}</p>
          </div>
        {/each}
      </div>
    {:else if status === 'notfound'}
      <div class="p-4 border rounded-md bg-red-50 border-red-200 text-center">
        <p class="font-semibold text-red-700">No matching registered intermediary found.</p>
      </div>
    {:else if status === 'error'}
      <div class="p-4 border rounded-md bg-red-50 border-red-200 text-center">
        <p class="font-semibold text-red-700">Error: {errorMessage}</p>
      </div>
    {/if}
  </div>
</div>