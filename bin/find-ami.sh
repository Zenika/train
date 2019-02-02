#!/bin/sh

export REGIONS="AP_NORTHEAST_1 \
AP_SOUTHEAST_1 \
AP_SOUTHEAST_2 \
EU_CENTRAL_1 \
EU_WEST_1 \
SA_EAST_1 \
US_EAST_1 \
US_WEST_1 \
US_WEST_2"

for REGION in $REGIONS; do
  REGION_LOWER=$(echo $REGION | tr '[:upper:]' '[:lower:]' | tr '_' '-')
  AMI=$(aws ec2 describe-images --owners 099720109477 --filters 'Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-????????' 'Name=state,Values=available' --output json --region=$REGION_LOWER | jq -r '.Images | sort_by(-.CreationDate) | .[0].ImageId' 2>/dev/null)
  echo "$REGION:"
  echo "'Ubuntu-18.04': '$AMI',"
done