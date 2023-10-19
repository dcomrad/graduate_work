#!/bin/bash

docker exec -it ugc_mongocfg1 bash -c 'echo "rs.initiate({_id: \"mongors1conf\", configsvr: true, members: [{_id: 0, host: \"ugc_mongocfg1\"}, {_id: 1, host: \"ugc_mongocfg2\"}]})" | mongosh'
docker exec -it ugc_mongors1n1 bash -c 'echo "rs.initiate({_id: \"mongors1\", members: [{_id: 0, host: \"ugc_mongors1n1\"}, {_id: 1, host: \"ugc_mongors1n2\"}, {_id: 2, host: \"ugc_mongors1n3\"}]})" | mongosh'

sleep 15

docker exec -it ugc_mongos1 bash -c 'echo "sh.addShard(\"mongors1/ugc_mongors1n1\")" | mongosh'

sleep 15

docker exec -it ugc_mongos1 bash -c 'echo "sh.enableSharding(\"ugc\")" | mongosh'
docker exec -it ugc_mongos1 bash -c 'echo "sh.shardCollection(\"ugc.bookmarks\", {\"user_id\": \"hashed\"})" | mongosh'
docker exec -it ugc_mongos1 bash -c 'echo "sh.shardCollection(\"ugc.movies_rating\", {\"film_id\": \"hashed\"})" | mongosh'
docker exec -it ugc_mongos1 bash -c 'echo "sh.shardCollection(\"ugc.reviews\", {\"film_id\": \"hashed\"})" | mongosh'
docker exec -it ugc_mongos1 bash -c 'echo "sh.shardCollection(\"ugc.reviews_rating\", {\"review_id\": \"hashed\"})" | mongosh'