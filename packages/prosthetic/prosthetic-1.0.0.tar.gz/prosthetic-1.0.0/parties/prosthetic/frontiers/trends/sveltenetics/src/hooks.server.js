


/** @type {import('@sveltejs/kit').Handle} */
export async function handle ({ event, resolve }) {
	// console.log ("hooks.server.js")
	console.log (event.url)
	

	// Apply CORS header for API routes
	if (event.url.pathname.startsWith ('/api')) {
		// Adjust the origin as needed. '*' allows any origin
		return new Response(null, {
			headers: {
				'Access-Control-Allow-Origin': '*',
				'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
				'Access-Control-Allow-Headers': 'Content-Type, Authorization',
			},
		});
	}

	const response = await resolve (event);
	return response;
}
