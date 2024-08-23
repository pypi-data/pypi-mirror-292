
<script>

import { onMount, onDestroy, beforeUpdate } from 'svelte'

import { ask_for_freight } from '$lib/Behavior/Trucks'
const { mongo_address } = ask_for_freight ();

console.info ({ mongo_address })

import { ask_trend_count } from '$lib/trends_mongo/ask_count.mongo.js'

let trends_vernacular = []
onMount (async () => {
	const { enhanced } = await ask_trend_count ()
	console.info ({ enhanced })
	
	trends_vernacular = enhanced.trends;
})

const parse_array = (the_array) => {
	return the_array.join (", ")
}

</script>


<div>
	<header>trends</header>
	{#each trends_vernacular as vernacular }
		<div style="display: none">{ JSON.stringify (vernacular, null, 4) }</div>
		<div
			class="card"
			style="
				margin: 12px 0;
				padding: 12px;
			"
		>
			<span class="badge variant-soft">
				<span>domain</span>
				<span class="badge variant-filled">{ vernacular.domain }</span>
			</span>
			
			<span class="badge variant-soft-warning">
				<span>names</span>
				{#if Array.isArray (vernacular.names) && vernacular.names.length >= 1}
				{#each vernacular.names as name }
					<span class="badge variant-filled">{ name }</span>
				{/each}
				{/if}
			</span>
			
			<span class="badge variant-soft-warning">
				<span>cautions</span>
				{#if Array.isArray (vernacular.cautions) && vernacular.cautions.length >= 1}
				{#each vernacular.cautions as caution }
					<span class="badge variant-filled-warning">{ caution }</span>
				{/each}
				{/if}
			</span>
			
			<span class="badge variant-soft">
				<span>topics</span>
				{#if Array.isArray (vernacular.topics) && vernacular.topics.length >= 1}
				{#each vernacular.topics as topic }
					<span class="badge variant-filled">{ topic }</span>
				{/each}
				{/if}
			</span>
			
		</div>
	{/each}
</div>