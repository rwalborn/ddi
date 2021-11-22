#!/bin/bash
#
# Script to check memory usage on Linux. Ignores memory used by disk cache.
#
# Requires the bc command
#
print_help() {
    echo "Usage:"
    echo "[-w] Warning level as a percentage"
    echo "[-c] Critical level as a percentage"
    exit 0
}

while test -n "$1"; do
    case "$1" in
        --help|-h)
            print_help
            exit 0
            ;;
        -w)
            warn_level=$2
            shift
            ;;
        -c)
            critical_level=$2
            shift
            ;;
        *)
            echo "Unknown Argument: $1"
            print_help
            exit 3
            ;;
    esac
    shift
done

if [ "$warn_level" == "" ]; then
    echo "No Warning Level Specified"
    print_help
    exit 3;
fi

if [ "$critical_level" == "" ]; then
    echo "No Critical Level Specified"
    print_help
    exit 3;
fi

free=`free -m | grep "buffers/cache" | awk '{print $4}'`
used=` free -m | grep "buffers/cache" | awk '{print $3}'`

total=$(($free+$used))

result=$(echo "$used / $total * 100" | bc -l | xargs printf "%1.2f" )

if [ $(bc <<< "$result < $warn_level") -eq 1 ]; then
    echo "Memory OK. $result% used. | free=$free, used=$used, total=$total"
    exit 0;
elif [ $(bc <<< "$result >= $warn_level") -eq 1 ] && [ $(bc <<< "$result < $critical_level") -eq 1 ]; then
    echo "Memory WARNING. $result% used. | free=$free, used=$used, total=$total"
    exit 1;
elif [ $(bc <<< "$result >= $critical_level") -eq 1 ]; then
    echo "Memory CRITICAL. $result% used. | free=$free, used=$used, total=$total"
    exit 2;
fi
