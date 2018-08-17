BEGIN TRANSACTION;
CREATE TABLE "aoi" (
        `name`  TEXT NOT NULL,
        `task`  INTEGER NOT NULL,
        `dynamic`       INTEGER,
        `polygon`       BLOB,
        PRIMARY KEY(`name`,`task`)
);
INSERT INTO "aoi" VALUES('text',62,NULL,'[(148,203),(148,558),(583,558),(583,203)]');
INSERT INTO "aoi" VALUES('text',3,NULL,'[(147,204),(147,880),(583,880),(583,204)]');
INSERT INTO "aoi" VALUES('vis',62,'','[(630,74),(630,466),(1083,466),(1083,74)]');
INSERT INTO "aoi" VALUES('legend',62,'','[(658,502),(658,553),(1072,553),(1072,502)]');
INSERT INTO "aoi" VALUES('legend',3,'','[(772,173),(772,215),(962,215),(962,173)]');
INSERT INTO "aoi" VALUES('vis',3,'','[(632,224),(632,622),(1070,622),(1070,224)]');
INSERT INTO "aoi" VALUES('legend',5,'','[(754,192),(754,217),(1055,217),(1055,192)]');
INSERT INTO "aoi" VALUES('vis',5,NULL,'[(620,228),(620,609),(1039,609),(1039,228)]');
INSERT INTO "aoi" VALUES('text',5,NULL,'[(149,205),(149,929),(585,929),(585,205)]');
INSERT INTO "aoi" VALUES('legend',9,NULL,'[(694,173),(694,222),(964,222),(964,173)]');
INSERT INTO "aoi" VALUES('vis',9,NULL,'[(622,226),(622,421),(1024,421),(1024,223)]');
INSERT INTO "aoi" VALUES('text',9,NULL,'[(150,205),(150,531),(581,531),(581,205)]');
INSERT INTO "aoi" VALUES('text',11,'','[(151,234),(151,510),(581,510),(581,234)]');
INSERT INTO "aoi" VALUES('vis',11,'','[(614,86),(614,465),(1152,465),(1152,86)]');
INSERT INTO "aoi" VALUES('legend',11,'','[(672,121),(672,185),(759,185),(759,121)]');
INSERT INTO "aoi" VALUES('text',18,'','[(151,185),(151,722),(585,722),(585,175)]');
INSERT INTO "aoi" VALUES('vis',18,'','[(606,144),(606,449),(1186,449),(1186,144)]');
INSERT INTO "aoi" VALUES('legend',18,'','[(1073,168),(1073,230),(1149,230),(1149,168)]');
INSERT INTO "aoi" VALUES('text',27,'','[(150,174),(150,549),(580,549),(580,174)]');
INSERT INTO "aoi" VALUES('vis',27,'','[(611,152),(611,555),(897,555),(897,152)]');
INSERT INTO "aoi" VALUES('legend',27,'','[(637,131),(637,149),(896,149),(896,131)]');
INSERT INTO "aoi" VALUES('text',28,'','[(150,175),(150,473),(582,473),(582,175)]');
INSERT INTO "aoi" VALUES('vis',28,NULL,'[(606,154),(606,557),(892,557),(892,154)]');
INSERT INTO "aoi" VALUES('legend',28,NULL,'[(636,135),(636,154),(899,154),(899,135)]');
INSERT INTO "aoi" VALUES('text',30,'','[(148,173),(148,351),(580,351),(580,173)]');
INSERT INTO "aoi" VALUES('vis',30,NULL,'[(602,146),(602,539),(899,539),(899,146)]');
INSERT INTO "aoi" VALUES('legend',30,NULL,'[(674,115),(674,146),(883,146),(883,115)]');
INSERT INTO "aoi" VALUES('text',60,NULL,'[(149,204),(149,378),(582,378),(582,204)]');
INSERT INTO "aoi" VALUES('vis',60,NULL,'[(598,72),(598,474),(1075,474),(1075,72)]');
INSERT INTO "aoi" VALUES('legend',60,NULL,'[(641,479),(641,527),(886,527),(886,479)]');
INSERT INTO "aoi" VALUES('text',72,NULL,'[(146,172),(146,425),(585,425),(585,172)]');
INSERT INTO "aoi" VALUES('vis',72,NULL,'[(599,125),(599,357),(1018,357),(1018,125)]');
INSERT INTO "aoi" VALUES('legend',72,NULL,'[(939,223),(939,302),(1018,302),(1018,223)]');
CREATE TABLE intervention_state ( `intervention` TEXT, `active` INTEGER, time_stamp INTEGER, occurences INTEGER, PRIMARY KEY(`intervention`));
INSERT INTO "intervention_state" VALUES('legend_intervention',1,1534542154334426,1);
CREATE TABLE legend_fix ( `id` INTEGER, `time_start` INTEGER, `time_end` INTEGER, `duration` INTEGER, PRIMARY KEY(`id`) );
CREATE TABLE rule_state ( `rule` TEXT, time_stamp INTEGER, occurences INTEGER, PRIMARY KEY(`rule`));
INSERT INTO "rule_state" VALUES('legend_11',1534542154334426,1);
CREATE TABLE text_fix ( `id` INTEGER, `time_start` INTEGER, `time_end` INTEGER, `duration` INTEGER, PRIMARY KEY(`id`) );
INSERT INTO "text_fix" VALUES(1,1534542102899976,1534542103016573,116597);
INSERT INTO "text_fix" VALUES(2,1534542103041593,1534542103283028,241435);
INSERT INTO "text_fix" VALUES(3,1534542110610614,1534542110718851,108237);
INSERT INTO "text_fix" VALUES(4,1534542110868703,1534542111018559,149856);
INSERT INTO "text_fix" VALUES(5,1534542134516851,1534542134625093,108242);
INSERT INTO "text_fix" VALUES(7,1534542183661323,1534542183936169,274846);
INSERT INTO "text_fix" VALUES(11,1534542190947368,1534542191163873,216505);
INSERT INTO "text_fix" VALUES(12,1534542191172083,1534542191396938,224855);
INSERT INTO "text_fix" VALUES(15,1534542191913250,1534542192129719,216469);
INSERT INTO "text_fix" VALUES(16,1534542192171331,1534542192279699,108368);
INSERT INTO "text_fix" VALUES(17,1534542192496165,1534542192654396,158231);
INSERT INTO "text_fix" VALUES(18,1534542192671018,1534542192895873,224855);
INSERT INTO "text_fix" VALUES(19,1534542192995734,1534542193112340,116606);
INSERT INTO "text_fix" VALUES(20,1534542193120711,1534542193403796,283085);
INSERT INTO "text_fix" VALUES(21,1534542193412173,1534542193562033,149860);
INSERT INTO "text_fix" VALUES(22,1534542193587023,1534542193795128,208105);
INSERT INTO "text_fix" VALUES(23,1534542193820116,1534542194019968,199852);
INSERT INTO "text_fix" VALUES(24,1534542194036591,1534542194278191,241600);
INSERT INTO "text_fix" VALUES(25,1534542194494667,1534542194761128,266461);
INSERT INTO "text_fix" VALUES(26,1534542194777748,1534542194927600,149852);
INSERT INTO "text_fix" VALUES(27,1534542194944350,1534542195177441,233091);
INSERT INTO "text_fix" VALUES(28,1534542195185813,1534542195310678,124865);
CREATE TABLE "user_state" (
	`event_name`	TEXT NOT NULL,
	`type`	TEXT,
	`aoi`	TEXT,
	`feature`	TEXT,
	PRIMARY KEY(`event_name`)
);
INSERT INTO "user_state" VALUES('text_fix','fix','text',NULL);
INSERT INTO "user_state" VALUES('pupil','emdat','vis','meanpupilsize');
INSERT INTO "user_state" VALUES('vis_fix','fix','vis',NULL);
INSERT INTO "user_state" VALUES('legend_fix','fix','legend',NULL);
CREATE TABLE "user_state_task" (
        `event_name`    TEXT,
        `task`  INTEGER,
        PRIMARY KEY(`event_name`,`task`)
);
INSERT INTO "user_state_task" VALUES('text_fix',62);
INSERT INTO "user_state_task" VALUES('vis_fix',62);
INSERT INTO "user_state_task" VALUES('legend_fix',62);
INSERT INTO "user_state_task" VALUES('legend_fix',3);
INSERT INTO "user_state_task" VALUES('vis_fix',3);
INSERT INTO "user_state_task" VALUES('text_fix',3);
INSERT INTO "user_state_task" VALUES('legend_fix',5);
INSERT INTO "user_state_task" VALUES('text_fix',5);
INSERT INTO "user_state_task" VALUES('vis_fix',5);
INSERT INTO "user_state_task" VALUES('legend_fix',9);
INSERT INTO "user_state_task" VALUES('vis_fix',9);
INSERT INTO "user_state_task" VALUES('text_fix',9);
INSERT INTO "user_state_task" VALUES('text_fix',11);
INSERT INTO "user_state_task" VALUES('legend_fix',11);
INSERT INTO "user_state_task" VALUES('vis_fix',11);
INSERT INTO "user_state_task" VALUES('text_fix',18);
INSERT INTO "user_state_task" VALUES('vis_fix',18);
INSERT INTO "user_state_task" VALUES('legend_fix',18);
INSERT INTO "user_state_task" VALUES('text_fix',27);
INSERT INTO "user_state_task" VALUES('vis_fix',27);
INSERT INTO "user_state_task" VALUES('legend_fix',27);
INSERT INTO "user_state_task" VALUES('text_fix',28);
INSERT INTO "user_state_task" VALUES('vis_fix',28);
INSERT INTO "user_state_task" VALUES('legend_fix',28);
INSERT INTO "user_state_task" VALUES('text_fix',30);
INSERT INTO "user_state_task" VALUES('vis_fix',30);
INSERT INTO "user_state_task" VALUES('legend_fix',30);
INSERT INTO "user_state_task" VALUES('text_fix',60);
INSERT INTO "user_state_task" VALUES('vis_fix',60);
INSERT INTO "user_state_task" VALUES('legend_fix',60);
INSERT INTO "user_state_task" VALUES('text_fix',72);
INSERT INTO "user_state_task" VALUES('vis_fix',72);
INSERT INTO "user_state_task" VALUES('legend_fix',72);
CREATE TABLE vis_fix ( `id` INTEGER, `time_start` INTEGER, `time_end` INTEGER, `duration` INTEGER, PRIMARY KEY(`id`) );
INSERT INTO "vis_fix" VALUES(6,1534542154217944,1534542154334426,116482);
INSERT INTO "vis_fix" VALUES(8,1534542184510697,1534542184693924,183227);
INSERT INTO "vis_fix" VALUES(9,1534542190114628,1534542190239604,124976);
INSERT INTO "vis_fix" VALUES(10,1534542190797390,1534542190930622,133232);
INSERT INTO "vis_fix" VALUES(13,1534542191413686,1534542191713400,299714);
INSERT INTO "vis_fix" VALUES(14,1534542191763397,1534542191896627,133230);
COMMIT;
