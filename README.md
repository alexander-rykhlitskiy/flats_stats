# Flats stats

### Export flats to csv
```bash
psql -U postgres -d gethataby_development -c "COPY (SELECT id, price, rooms_number, updated_at, coords[0] as lat, coords[1] as lon, agent, address, created_at from flats) to '/tmp/flats.csv' DELIMITER ',' CSV HEADER" && cp /tmp/flats.csv ./
```

### Run streamlit server
```bash
docker build -t flats_stats .

docker run -v $(pwd):/app -it --rm -p 8501:8501 flats_stats
```

#### Run in "production"
```bash
docker run -d --restart always -v $(pwd):/app -it -p 8501:8501 flats_stats
```
Add to `.streamlit/config.toml`
```
[browser]

serverAddress = "berlog.ga"
```
### Connect to streamlit container or run custom script
```bash
docker exec -it $(docker ps | grep flats_stats | awk '{print $1}') /bin/bash
# or
docker run -v $(pwd):/app -it --rm flats_stats python
```

### Debugging
In your code
```python
import code; code.interact(local=dict(globals(), **locals()))
```

### Analysis
Hexagon map was used instead of heatmap as heatmap relies too much on number of points, but we need to measure the color of the point only by mean price in this region.

### TODO
1. Show values of colors. It can be done via
    1. map legend. Seems to be absent in Deck.gl, but can be built with custom layer or the info in the link below
    2. tooltip hovering the cell http://deck.gl/#/documentation/developer-guide/adding-interactivity?section=example-display-a-tooltip-for-hovered-object. Seems we need to get rid of streamlit to achieve it
2. Smarter way to remove duplicates. Do not remove second ad of the same flat, if the first one was created long ago (we can see price trend). Two flats with the same price and rooms_number can be at the same address.
3. Manually split flats into cells. It would allow to
    1. remove upper and lower percentiles of ads by count so it will affect colors distribution by cells. Current Deck.gl implementation leaves initial colors after filtering by elevation (count)
    2. use logarithmic not linear color scale
4. Remove upper and lower percentiles of ads by price in groups splitted by rooms_number. E.g. $150 one-room flat is ok, but $150 two-room flat seems to be fake and can be removed
