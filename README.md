# Flats stats

### Export flats to csv
```bash
psql -U postgres -d gethataby_development -c "COPY (SELECT id, price, rooms_number, updated_at, coords[0] as lat, coords[1] as lon, agent from flats) to '/tmp/flats.csv' DELIMITER ',' CSV HEADER" && cp /tmp/flats.csv ./
```

### Run streamit server
```bash
docker build -t flats_stats .

docker run -v $(pwd):/app -it --rm -p 8501:8501 flats_stats
```

### Connect to jupyter container or run custom script
```bash
docker exec -it $(docker ps | grep flats_stats | awk '{print $1}') /bin/bash

docker run -v $(pwd):/app -it --rm flats_stats
  python main.py
  ipython nbconvert --to html stats_by_dates.ipynb
```