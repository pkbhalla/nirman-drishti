"""Load real GeoSadak shapefiles (Habitation points, Proposal PMGSY-III lines) with pyshp. Assumes EPSG:4326 (check .prj)."""
import pandas as pd
def _read(path):
    import shapefile
    sf=shapefile.Reader(path); fields=[f[0] for f in sf.fields[1:]]
    return sf,fields
def load_habitations(shp_path, ommas_district_id=None):
    sf,f=_read(shp_path); rows=[]
    for sr in sf.iterShapeRecords():
        d=dict(zip(f,sr.record))
        if ommas_district_id is not None and d.get("DISTRICT_I")!=ommas_district_id: continue
        if not sr.shape.points: continue
        lon,lat=sr.shape.points[0]; d["lon"],d["lat"]=lon,lat; rows.append(d)
    df=pd.DataFrame(rows)
    return df.rename(columns={"DISTRICT_I":"DISTRICT_ID"})
def load_proposals(shp_path, lgd_district=None):
    sf,f=_read(shp_path); meta=[]; lines=[]
    for sr in sf.iterShapeRecords():
        d=dict(zip(f,sr.record))
        if lgd_district is not None and d.get("LGD_DISTRI")!=lgd_district: continue
        pts=sr.shape.points
        if len(pts)<2: continue
        parts=list(sr.shape.parts)+[len(pts)]
        for a,b in zip(parts[:-1],parts[1:]): lines.append((d["MRL_ID"],pts[a:b]))
        meta.append(d)
    return pd.DataFrame(meta),lines
