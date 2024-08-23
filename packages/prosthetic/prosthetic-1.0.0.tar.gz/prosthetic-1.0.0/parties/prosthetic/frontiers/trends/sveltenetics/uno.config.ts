

import { defineConfig } from 'unocss';
import presetWind from '@unocss/preset-wind';
import transformerVariantGroup from '@unocss/transformer-variant-group';
import transformerDirectives from '@unocss/transformer-directives';
import presetIcons from '@unocss/preset-icons';
 
import { presetAtoUI } from 'ato-ui/preset';
 
export default defineConfig({
    presets: [
        presetIcons({
            extraProperties: {
                display: 'inline-block',
                'vertical-align': 'middle'
            }
        }),
        presetWind(),
        presetAtoUI()
    ],
    transformers: [transformerVariantGroup(), transformerDirectives()]
});