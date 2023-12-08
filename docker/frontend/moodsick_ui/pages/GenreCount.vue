<template>
    <h1>
        Genre Count
    </h1>
    <div id="main" style="height:80vh; width:80vw">

    </div>
</template>

<script>
import * as echarts from 'echarts';

export default {
    mounted() {
        var chartDom = document.getElementById('main');
        var myChart = echarts.init(chartDom);
        var option;
        let xAxisColum = ['rock', 'hip-hop', 'blues', 'classical', 'metal', 'reggae', 'country', 'pop', 'disco']
        option = {
            xAxis: {
                type: 'category',
                name: 'Genres',
                data: xAxisColum
            },
            yAxis: {
                type: 'value',
                name: 'Count',
            },

            series: [
                {
                    data: [2, 1, 1, 0, 1, 1, 0, 1, 1],
                    type: 'bar'
                }
            ]
        };

        option && myChart.setOption(option);

    }
}
</script>

<style></style>



<!-- 
option = {
    xAxis: {
      type: 'category',
      name: 'Genres',
      data: ['rock', 'hip-hop', 'blues', 'classical', 'metal', 'reggae', 'country', 'pop', 'disco']
    },
    yAxis: {
      type: 'value',
      name: 'Count'
    },
    series: [
      {
        data: [2, 1, 1, 0, 1, 1, 0, 1, 1],
        type: 'line'
      }
    ]
  }; -->