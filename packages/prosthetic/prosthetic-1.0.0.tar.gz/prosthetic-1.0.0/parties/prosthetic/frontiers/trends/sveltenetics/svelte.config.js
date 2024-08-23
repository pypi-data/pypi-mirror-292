
// https://css-tricks.com/how-i-built-a-cross-platform-desktop-application-with-svelte-redis-and-rust/


// adapter-auto only supports some environments, see https://kit.svelte.dev/docs/adapter-auto for a list.
// If your environment is not supported, or you settled on a specific environment, switch out the adapter.
// See https://kit.svelte.dev/docs/adapters for more information about adapters.
// import adapter from '@sveltejs/adapter-auto';

//
//	This writes the platform to "build"
//		https://kit.svelte.dev/docs/adapter-static
//
import adapter_static from '@sveltejs/adapter-static';


import adapter_node from '@sveltejs/adapter-node';
import preprocess from 'svelte-preprocess';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	compilerOptions: {
		enableSourcemap: true,
	},

	
	
	kit: {
		
		// adapter: adapter_node (),
		
		adapter: adapter_static ({
			// base: "/built",
			
			// default options are shown. On some platforms
			// these options are set automatically — see below
			// pages: 'build',
			// assets: 'build',
			// fallback: undefined,
			
			fallback: 'index.html',
			
			// precompress: false,
			
			// strict: false,
			
			// alias: {
			// 	$assets: 'assets'
			//}
		}),
		
		
		
		csrf: {
			checkOrigin: false,
		}
	}
};

export default config;
