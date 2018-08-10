BEGIN TRANSACTION;
CREATE TABLE "rule_task" (
	`rule_name`	TEXT NOT NULL,
	`task`	INTEGER
);
INSERT INTO `rule_task` (rule_name,task) VALUES ('ref_1_rule',1);
INSERT INTO `rule_task` (rule_name,task) VALUES ('legend_rule',1);
INSERT INTO `rule_task` (rule_name,task) VALUES ('ref_2_rule',1);
INSERT INTO `rule_task` (rule_name,task) VALUES ('ref_3_bar_4_rule',1);
INSERT INTO `rule_task` (rule_name,task) VALUES ('ref_4_bar_5_rule',1);
INSERT INTO `rule_task` (rule_name,task) VALUES ('ref_3_bar_3_rule',1);
INSERT INTO `rule_task` (rule_name,task) VALUES ('ref_4_bar_6_rule',1);
CREATE TABLE "rule" (
	`name`	TEXT NOT NULL,
	`delivery_sql_condition`	BLOB,
	`removal_sql_condition`	BLOB,
	`max_repeat`	INTEGER,
	`active_retrigger`	INTEGER,
	PRIMARY KEY(`name`)
);
INSERT INTO `rule`  VALUES ('legend_rule','Select
	case when count(*) > 0
		then 1
		else 0
	end result
From
(select * from text_fix TF, vis_fix VF
where TF.time_start < VF.time_start
group by VF.id
having count(TF.id) > 0);
','select 1 as result;','',NULL);
INSERT INTO `rule`  VALUES ('ref_1_rule','Select 1 as result;','select 1 as result;',NULL,NULL);
INSERT INTO `rule`  VALUES ('ref_2_rule','select 1 as result;','select 1 as result',NULL,NULL);
INSERT INTO `rule`  VALUES ('ref_3_bar_3_rule','Select 1 as result;','select 1 as result;','',NULL);
INSERT INTO `rule`  VALUES ('ref_4_bar_5_rule','Select 1 as result;','Select
	case when count(*) > 0
		then 1
		else 0
	end result
From
text_fix, intervention_state
where intervention_state.intervention = "bar_4_intervention"
and text_fix.time_end > intervention_state.time_stamp + 3000000;
',NULL,NULL);
INSERT INTO `rule`  VALUES ('ref_3_bar_4_rule','Select 1 as result;','select 1 as result',NULL,NULL);
INSERT INTO `rule`  VALUES ('ref_4_bar_6_rule','select 1 as result;','Select
	case when count(*) > 0
		then 1
		else 0
	end result
From
text_fix, intervention_state
where intervention_state.intervention = "bar_4_intervention"
and text_fix.time_end > intervention_state.time_stamp + 3000000;',NULL,NULL);
CREATE TABLE "rule_delivery_trigger" (
	`rule_name`	TEXT NOT NULL,
	`delivery_trigger_event`	TEXT
);
CREATE TABLE "rule_removal_trigger" (
	`rule_name`	TEXT NOT NULL,
	`removal_trigger_event`	TEXT
);
CREATE TABLE "rule_intervention_payload" (
	`rule_name` TEXT NOT NULL,
	`intervention_name` TEXT
);
CREATE TABLE "intervention" (
	`name`	TEXT NOT NULL,
	`max_repeat`	INTEGER,
	`function`	BLOB NOT NULL,
	`arguments`	BLOB,
	`delivery_delay`	INTEGER,
	`transition_in`	INTEGER,
	`transition_out`	INTEGER,
	PRIMARY KEY(`name`)
);
INSERT INTO `intervention` VALUES ('bar_1_intervention', NULL,'highlightVisOnly','{"type": "reference", "id": 5, "bold": true, "bold_thickness": 3, "desat": true, "color": "green", "arrow": false}',10,500,500);
INSERT INTO `intervention` VALUES ('legend_intervention',1,'highlightLegend','{"type": "legend", "color": "blue", "bold": true, "bold_thickness": 5, "desat": false, "arrow": false, "arrow_direction": "bottom"}',0,500,500);
INSERT INTO `intervention` VALUES ('bar_2_intervention',NULL,'highlightVisOnly','{"type": "reference", "id":2, "bold": true, "bold_thickness": 3, "desat": true, "color": "green", "arrow": false}
',0,500,500);
INSERT INTO `intervention` VALUES ('bar_3_intervention','','highlightVisOnly','{"type": "reference", "id":3, "bold": true, "bold_thickness": 3, "desat": true, "color": "green", "arrow": false}',0,500,500);
INSERT INTO `intervention` VALUES ('bar_5_intervention',NULL,'highlightVisOnly','{"type": "reference", "id": 4, "bold": true, "bold_thickness": 3, "desat": true, "color": "green", "arrow": false}',10,500,500);
INSERT INTO `intervention` VALUES ('bar_4_intervention',NULL,'highlightVisOnly','{"type": "reference", "id": 0, "bold": true, "bold_thickness": 3, "desat": true, "color": "green", "arrow": false}',0,500,500);
INSERT INTO `intervention` VALUES ('bar_6_intervention',NULL,'highlightVisOnly','{"type": "reference", "id": 1, "bold": true, "bold_thickness": 3, "desat": true, "color": "green", "arrow": false}',0,500,500);
COMMIT;
