-- Database: music

-- DROP DATABASE music;
	
CREATE OR REPLACE FUNCTION log_account_creation_function() RETURNS TRIGGER AS
$BODY$
DECLARE
	uUsername text;
BEGIN
	uUsername = new."uUsername";
	INSERT INTO music_log("uUsername", "lDate", "lMessage")
	VALUES(uUsername, NOW(), 'Account Created');
	RETURN new;
END;
$BODY$
language plpgsql;

DROP TRIGGER IF EXISTS log_account_creation
ON public.users;

CREATE TRIGGER log_account_creation
	AFTER INSERT ON users
	FOR EACH ROW
	EXECUTE PROCEDURE log_account_creation_function();