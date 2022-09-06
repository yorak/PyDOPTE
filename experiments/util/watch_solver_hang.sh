#/bin/bash
while true; do 
  rpid=`ps -u juherask r | grep param_ils_2_3_run.rb | awk '{ if ( $4 > 1) print $1}'`
  if [ -n "$rpid" ]; then
    echo $rpid
    kill $rpid
  fi
  rpid=`ps -u juherask r | grep vrpsd. | awk '{ if ( $4 > 1) print $1}'`
  if [ -n "$rpid" ]; then
    echo $rpid
    kill $rpid
  fi
  sleep 10
  rpid=`ps -u juherask r | grep vrp_ej | awk '{ if ( $4 > 1) print $1}'`
  if [ -n "$rpid" ]; then
    echo $rpid
    kill $rpid
  fi
  sleep 10
done
