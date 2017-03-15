-twitts table
create table tweets 
(
t_id bigint,
uname text,
n_id bigint,
loc_text text,
u_img text,
lat float,
lon float,
date_str text,
content text,
clas text
);
--create geometry column and populate it
select AddGeometryColumn('tweets','geom',4326,'Point',2);
update tweets set geom = ST_SetSRID(ST_MakePoint(lon,lat),4326);

--Spatial index
CREATE INDEX tweets_idx_gist ON tweets USING gist(geom);

--Unique identifier and index:
CREATE SEQUENCE tweet_ids;
ALTER TABLE tweets ADD id INT UNIQUE;
UPDATE tweets SET id = NEXTVAL('tweet_ids');

--Set date_str as real date
alter table tweets
alter column date_str type timestamp
using date_str::timestamptz

--Copy the central region to a table:
create table extent as 
select 1, ST_SetSRID(ST_Extent(geom),4326) as geom FROM denue;

create table tweets_centro as select t.*
from tweets t, extent d
where st_intersects(t.geom,d.geom ) 
--Index the table.
alter table tweets_centro
add  unique (id);
create index tweet_centro_gist on tweets_centro using gist (geom)
--Reproject to planar coordinates.
ALTER TABLE tweets_centro 
   ALTER COLUMN geom 
   TYPE Geometry(Point, 32614) 
   USING ST_Transform(geom, 32614);
--Also reproject denue:
ALTER TABLE denue 
   ALTER COLUMN geom 
   TYPE Geometry(Point, 32614) 
   USING ST_Transform(geom, 32614);

--Drop unnedded columns from denue:
alter table denue
drop column raz_social,
drop column nombre_act,
drop column tipo_vial,
drop column nom_vial,
drop column tipo_v_e_1,
drop column nom_v_e_1,
drop column tipo_v_e_2,
drop column nom_v_e_2,
drop column tipo_v_e_3,
drop column nom_v_e_3,
drop column numero_ext,
drop column letra_ext,
drop column edificio,
drop column edificio_e,
drop column numero_int,
drop column letra_int,
drop column tipo_asent,
drop column nomb_asent,
drop column nom_cencom,
drop column num_local,
drop column telefono,
drop column correoelec,
drop column www;

-- Amount of jobs per economic unit
alter table denue add column avg_jobs int;

update denue set avg_jobs =
case 
	when per_ocu like '0%' then 2
	when per_ocu like '6%' then 5
	when per_ocu like '11%' then 15
	when per_ocu like '31%' then 25
	when per_ocu like '51%' then 50
	when per_ocu like '101%' then 175
	when per_ocu like '251%' then 251
	else  0
end;

--block level id for each unit.
alter table denue add column cve_mza text;
update denue set cve_mza = cve_ent || cve_mun || cve_loc || ageb || manzana;

-- Set activity classes:
alter table denue add column id_act text;

update denue set id_act =
case 
	when codigo_act like '%31' or codigo_act like '%32' or codigo_act like '%33'then 'IN'
	when codigo_act like '461%' or codigo_act like '462%' or codigo_act like '463%' or 
				codigo_act like '464%' or codigo_act like '465%' or codigo_act like '466%'then 'CO'
	when codigo_act like '48111%' or  codigo_act like '485210' then 'TR'
	when codigo_act like '51%' or codigo_act like '521%' or codigo_act like '523%' or codigo_act like '524%' or codigo_act like '5312%'
				or codigo_act like '5313%' or codigo_act like '541%' or codigo_act like '55%' then 'OF'
	when codigo_act like '6111%' or codigo_act like '6115%' then 'ES'
	when codigo_act like '621%' or codigo_act like '622%'  then 'SA'
	when  codigo_act like '711121%' or codigo_act like '71212%'  or codigo_act like '7132%'  or codigo_act like '7139%'
				or codigo_act like '7211%' or codigo_act like '7224%' or codigo_act like '7225%' then 'OC'
	when codigo_act like '931%' or codigo_act like '622%'  then 'GO'
	else  'NO CLASS'
end 
--create an index for id_act column:
create index denue_id_act_idex on denue (id_act)

--Update tweets table with activity count (one of these per activity type)
alter table tweets add column industria int;

update tweets_centro set industria =  foo.cuantos
from 
(
select  t.id, count(d.id) -1 as cuantos
from tweets_centro t, denue d
where st_dwithin(t.geom,d.geom,500) and d.id_act like'IN'
group by t.id) as foo
where tweets_centro.id = foo.id

--For transport is a little different: we'll grab the airports from one table:
update tweets_centro set transporte_count =  foo.cuantos
from 
(
select  t.id, count(d.id) -1 as cuantos
from tweets_centro t, aeropuertos d
where st_dwithin(t.geom,d.geom,500)
group by t.id) as foo
where tweets_centro.id = foo.id

--And Bus stations from denue, then we'll jus add to the count:
update tweets_centro set transporte_count =  transporte_count + foo.cuantos
from 
(
select  t.id, count(d.id) -1 as cuantos
from tweets_centro t, 
    (select * from denue  where tipocencom like 'CENTRAL CAMIONERA') as d
where st_dwithin(t.geom,d.geom,500)
group by t.id) as foo
where tweets_centro.id = foo.id

-- Compute jobs per city block and store it in manzanas table:
create index manzanas_cvgeo_idx on manzanas (cvegeo);
create index denue_cv_mza_idx on denue (cve_mza);

alter table manzanas add column jobs int;

update manzanas m set jobs = sub.jobs
from
    (
        select cve_mza, sum(avg_jobs) as jobs
        from denue
        group by cve_mza
    ) as sub
where m.cvegeo = sub.cve_mza

-- Compute job to housing ratio:
update manzanas set job_housing = jobs::float/viv_0::float
where cvegeo like '29%' and jobs is not null and viv_0 !=0

--create boolean column for clase transporte:
alter table tweets_centro add column trans_bool boolean;
update tweets_centro set trans_bool = false where transporte_count is null
update tweets_centro set trans_bool = true where transporte_count is not  null
-- Add interval column and classify accordint to weekday and time:
alter table tweets_centro add column intervalo text;

update tweets_centro set intervalo =
case 
    when date_str::time >= '05:00:00' and  date_str::time < '10:00:00' then to_char(date_str, 'dy') || '.' || '01'
    when date_str::time >= '10:00:00' and  date_str::time < '14:00:00' then to_char(date_str, 'dy') || '.' || '02'
    when date_str::time >= '14:00:00' and  date_str::time < '16:00:00' then to_char(date_str, 'dy') || '.' || '03'
    when date_str::time >= '16:00:00' and  date_str::time < '19:00:00' then to_char(date_str, 'dy') || '.' || '04'
    when date_str::time >= '19:00:00' and  date_str::time < '22:00:00' then to_char(date_str, 'dy') || '.' || '05'
    when date_str::time >= '22:00:00' and  date_str::time <= '23:59:59' then to_char(date_str, 'dy') || '.' || '06'
    when date_str::time >= '00:00:00' and  date_str::time < '05:00:00' then to_char(date_str, 'dy') || '.' || '01'
    else 'n/a'
end;

--Store block_id in tweets table for those twits that are inside blocks:
alter table tweets_centro add column cve_mza text;

update tweets_centro set cve_mza = sub.cvegeo
from 
(select t.id, m.cvegeoinventario_vivienda
from tweets_centro t, manzanas m
where st_intersects(m.geom,t.geom)) as sub
where sub.id = tweets_centro.id

-- For thos thad didnt lien within city blocks but are near enough:
update tweets_centro set cve_maza = sub.cvegeo
from(
select t.id, r.cvegeo, dist
from (select * from tweets_centro where cve_maza is null) as t
cross join lateral
(
select m.cvegeo, st_distance(m.geom,t.geom) as dist
from manzanas m
order by m.geom <-> t.geom
limit 1
) as r)as sub
where tweets_centro.id = sub.id and sub.dist <= 500.0

--Add job to housign to tuits table.
alter table tweets_centro add column job_housing float;

update tweets_centro set job_housing = sub.job_housing
from
(select job_housing, cvegeo from manzanas) as sub
where tweets_centro.cve_maza = sub.cvegeo

--Create table for inventario_vivienda
create table inventario_vivienda
(
id int,
ent text,
nom_ent text,
mun text,
nom_mun text,
loc text,
nom_loc text,
ageb text,
mza text,
conjhab int,
recucall int,
banqueta int,
guarnici int,
arboles int,
rampas int,
alumpub int,
senaliza int,
telpub int,
drenajep int,
transcol int,
acesoper int,
acesoaut int,
puessemi int,
puesambu int,
vivtot int, 
tvivhab int,
tvivparhab int,
vph_depto int,
pobtot int,
cve_mza text
)


--Export balanced sample as csv

copy 
(
select t_id,uname,loc_text,replace(content,'"',' ') as content, clas, id, industria, 
comercio, oficinas, escuelas, salud, ocio, gobierno, trans_bool as trans, intervalo, job_housing 
from tweets_centro 
where job_housing is not null and clas = 'NEU'
order by random()
limit 5000
)
to '/var/pg_shared/muestra_NEU.csv'
 WITH (FORMAT CSV, HEADER TRUE, FORCE_QUOTE *, DELIMITER '|')
 
