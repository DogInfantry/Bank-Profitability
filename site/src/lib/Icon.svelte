<script lang="ts">
  import { icons, type IconName } from './icons';
  let { name, label = '' }: { name: IconName; label?: string } = $props();
</script>
<span class="icon" role={label ? 'img' : undefined} aria-label={label || undefined} aria-hidden={label ? undefined : 'true'}>{@html icons[name]}</span>
