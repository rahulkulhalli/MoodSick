<template>
    <h1>
        Day of the week frequency
    </h1>
    <div id="main" style="height:80vh; width:90vw">

    </div>
</template>

<script>
import * as echarts from 'echarts';

export default{
    mounted(){
        var chartDom = document.getElementById('main');
var myChart = echarts.init(chartDom);
var option;

option = {
  xAxis: {
    type: 'category',
    name: 'Day of the week',
    data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  },
  yAxis: {
    type: 'value',
    name: 'Frequency',
  },
  
  series: [
    {
      data: [1, 2, 3, 4, 5, 6, 7],
      type: 'bar'
    }
  ]
};

option && myChart.setOption(option);

    }
}
</script>

<style>

</style>