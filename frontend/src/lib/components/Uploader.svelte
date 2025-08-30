<script lang="ts">
  export let title: string;
  export let description: string;
  export let endpoint: string;
  export let acceptedFileTypes: string;

  let file: File | null = null;
  let result: any = null;
  let status: 'idle' | 'uploading' | 'success' | 'error' = 'idle';
  let errorMessage = '';

  const handleFileSelect = (e: Event) => {
    const input = e.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      file = input.files[0];
      result = null;
      status = 'idle';
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    status = 'uploading';
    result = null;
    const formData = new FormData();
    formData.append('file', file);

    const backendUrl = 'http://127.0.0.1:8000'; // Local
    // const backendUrl = 'https://your-render-app-name.onrender.com'; // Production

    try {
      const response = await fetch(`${backendUrl}${endpoint}`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }
      result = await response.json();
      status = 'success';
    } catch (err) {
      status = 'error';
      errorMessage = err instanceof Error? err.message : 'An unknown error occurred.';
    }
  };
</script>

<div>
  <h2 class="text-2xl font-semibold mb-2 text-gray-700">{title}</h2>
  <p class="text-gray-600 mb-4">{description}</p>

  <div class="flex items-center space-x-4">
    <input
      type="file"
      on:change={handleFileSelect}
      accept={acceptedFileTypes}
      class="block w-full text-sm text-gray-500
             file:mr-4 file:py-2 file:px-4
             file:rounded-full file:border-0
             file:text-sm file:font-semibold
             file:bg-blue-50 file:text-blue-700
             hover:file:bg-blue-100"
    />
    <button
      on:click={handleUpload}
      disabled={!file || status === 'uploading'}
      class="px-4 py-2 bg-blue-600 text-white rounded-md disabled:bg-gray-400"
    >
      {#if status === 'uploading'}
        Analyzing...
      {:else}
        Analyze
      {/if}
    </button>
  </div>

  <div class="mt-6">
    {#if status === 'success'}
      <div class="p-4 border rounded-md bg-gray-50">
        <h3 class="font-semibold text-lg">Analysis Result:</h3>
        <pre class="bg-gray-100 p-2 rounded mt-2 text-sm overflow-x-auto">
          {JSON.stringify(result, null, 2)}
        </pre>
      </div>
    {:else if status === 'error'}
      <div class="p-4 border rounded-md bg-red-50 border-red-200 text-center">
        <p class="font-semibold text-red-700">Error: {errorMessage}</p>
      </div>
    {/if}
  </div>
</div>