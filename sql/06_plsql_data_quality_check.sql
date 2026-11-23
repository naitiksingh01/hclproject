-- =====================================================================
-- 06 - PL/SQL data-quality gate (bonus): raises an error if the load is bad
-- =====================================================================
SET SERVEROUTPUT ON
CREATE OR REPLACE PROCEDURE sp_check_sales_load (p_expected_rows IN NUMBER, p_expected_total IN NUMBER) AS
  v_rows   NUMBER;
  v_total  NUMBER;
  v_orph   NUMBER;
BEGIN
  SELECT COUNT(*), SUM(sales) INTO v_rows, v_total FROM fact_sales;
  SELECT COUNT(*) INTO v_orph FROM fact_sales f
   WHERE NOT EXISTS (SELECT 1 FROM dim_product p WHERE p.product_id = f.product_id);
  DBMS_OUTPUT.PUT_LINE('Rows: '||v_rows||'  Total: '||v_total||'  Orphans: '||v_orph);
  IF v_rows <> p_expected_rows THEN
     RAISE_APPLICATION_ERROR(-20001,'Row count mismatch: '||v_rows||' vs '||p_expected_rows);
  END IF;
  IF ABS(v_total - p_expected_total) / p_expected_total > 0.001 THEN
     RAISE_APPLICATION_ERROR(-20002,'Total sales differs by more than 0.1 percent');
  END IF;
  IF v_orph > 0 THEN RAISE_APPLICATION_ERROR(-20003,'Orphan product keys found'); END IF;
  DBMS_OUTPUT.PUT_LINE('LOAD CHECK PASSED');
END;
/
EXEC sp_check_sales_load(15181, 241053486.78);
