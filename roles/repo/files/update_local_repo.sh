#!/bin/bash

# pull down any new files
/usr/bin/aws s3 sync s3://ddi-ops-repo/x86_64 /mnt/ephemeral/repo/DDI/6/DDI/
/usr/bin/aws s3 sync s3://ddi-releases-repo/x86_64 /mnt/ephemeral/repo/releases/6/DDI-RELEASES/

# The following two loops look like they could be combined, but they should not be.  S3 transfers have a certain amount of latency that's substantially higher than changing file pointers.  We pull down the files first and then clobber the metadata to minimize the amount of time that the metadata is out of sync with itself and/or being overwritten.  If we don't, we're likely to see occasional failures of RPM deployments.

# pull down metadata
for file in "filelists.xml.gz" "other.xml.gz" "primary.xml.gz" "repomd.xml"
do
  /usr/bin/aws s3 cp s3://ddi-ops-repo/x86_64/repodata/$file  /mnt/ephemeral/repo/DDI/6/DDI/repodata/$file.new
  /usr/bin/aws s3 cp s3://ddi-releases-repo/x86_64/repodata/$file /mnt/ephemeral/repo/releases/6/DDI-RELEASES/repodata/$file.new
done

# Clobber metadata with new metadata
for path in "/mnt/ephemeral/repo/DDI/6/DDI/repodata" "/mnt/ephemeral/repo/releases/6/DDI-RELEASES/repodata"
do
  for file in "filelists.xml.gz" "other.xml.gz" "primary.xml.gz" "repomd.xml"
  do
    mv $path/$file.new $path/$file
  done
done

# Clean up any deleted files
/usr/bin/aws s3 sync --delete s3://ddi-ops-repo/x86_64 /mnt/ephemeral/repo/DDI/6/DDI/
/usr/bin/aws s3 sync --delete s3://ddi-releases-repo/x86_64 /mnt/ephemeral/repo/releases/6/DDI-RELEASES/

