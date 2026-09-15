<template>
  <div>
    {{ foo * 10 + 'hi' }}
    <span
      v-text="foo * 10 + 'hi'"
      :id="foo + 'baz'"
      @click="onClick('hello')"
      @click.prevent="onClick('hello')">
      Hello
    </span>
  </div>
</template>

<script>
export default {
  data: () => ({
    foo: 'bar'
  })
}
</script>

<style>
div {
  color: red;
}
</style>
