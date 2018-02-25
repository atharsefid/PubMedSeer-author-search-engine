for dir in $1/*
 do
  for (( j=1; j<=4; j++ ))
   do
    echo $dir"/img_0"$j
    python processposfile.py $dir"/img_0"$j
  done
 done


