



// https://aptos.dev/en/build/apis/fullnode-rest-api-reference#tag/general/get/

/*
	import { ask_trend_count } from '$lib/trends_mongo/ask_count.mongo.js'
	const { enhanced } = await ask_trend_count ()
*/

import { ask_for_freight } from '$lib/Behavior/Trucks'

export const ask_trend_count = async () => {
	const { origin_address } = ask_for_freight ();
	const proceeds = await fetch (origin_address + "/monetary/trends/itemize");
	const enhanced = await proceeds.json ()

	return {
		enhanced
	};
}