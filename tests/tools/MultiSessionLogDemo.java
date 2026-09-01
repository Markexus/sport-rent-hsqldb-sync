import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;

public final class MultiSessionLogDemo {
    private static final String DATABASE_URL =
            "jdbc:hsqldb:file:hsqldb-data/multisession;shutdown=false";

    private MultiSessionLogDemo() {}

    public static void main(String[] args) throws Exception {
        Class.forName("org.hsqldb.jdbc.JDBCDriver");

        try (Connection admin = openConnection()) {
            prepareDatabase(admin);

            try (Connection first = openConnection(); Connection second = openConnection()) {
                first.setAutoCommit(false);
                second.setAutoCommit(false);

                System.out.println("Pierwsza sesja: " + sessionId(first));
                System.out.println("Druga sesja: " + sessionId(second));

                execute(
                        first,
                        "INSERT INTO RESERVATIONPOSITION VALUES "
                                + "(2001, '2026-10-01 10:00:00', '2026-10-03 18:00:00', "
                                + "3001, 4001, 5001, '0', 0, NULL, 0.23, 0, 0, 100, 100, 1, "
                                + "6001, 0)");
                execute(
                        second,
                        "INSERT INTO RESERVATIONPOSITION VALUES "
                                + "(2002, '2026-10-05 10:00:00', '2026-10-07 18:00:00', "
                                + "3002, 4002, 5002, '0', 0, NULL, 0.23, 0, 0, 80, 80, 1, "
                                + "6001, 1)");

                // Celowo zatwierdzamy w odwrotnej kolejności niż wykonaliśmy INSERT-y.
                second.commit();
                first.commit();

                System.out.println("Obie transakcje zatwierdzone.");
                System.out.println(
                        "Teraz, w drugim terminalu, odczytaj hsqldb-data/multisession.log.");
                System.out.println("Dopiero potem naciśnij Enter, aby wykonać SHUTDOWN.");
                System.in.read();
            }

            execute(admin, "SHUTDOWN");
        }
    }

    private static Connection openConnection() throws Exception {
        return DriverManager.getConnection(DATABASE_URL, "SA", "");
    }

    private static void prepareDatabase(Connection connection) throws Exception {
        execute(connection, "SET DATABASE TRANSACTION CONTROL MVCC");
        execute(connection, "DROP TABLE RESERVATIONPOSITION IF EXISTS");
        execute(
                connection,
                "CREATE MEMORY TABLE RESERVATIONPOSITION ("
                        + "ID BIGINT NOT NULL PRIMARY KEY, "
                        + "BEGINDATE TIMESTAMP, ENDDATE TIMESTAMP, "
                        + "RESERVATIONDOCUMENT_ID BIGINT, RENTOBJECT_ID BIGINT, "
                        + "CUSTOMER_ID BIGINT, USEBONUSRATER BIT(1), "
                        + "BONUSTIME BIGINT DEFAULT 0, DIN DOUBLE, "
                        + "STORETAXHIB DOUBLE DEFAULT 0.22, PERCENTDISCOUNTHIB DOUBLE, "
                        + "VALUEDISCOUNTHIB DOUBLE, PRICE DOUBLE, PAYMENT DOUBLE, "
                        + "STATUS INTEGER DEFAULT 0, RATER_ID BIGINT, LISTINDEX INTEGER)");
        execute(connection, "CHECKPOINT");
    }

    private static long sessionId(Connection connection) throws Exception {
        try (Statement statement = connection.createStatement();
                ResultSet result = statement.executeQuery("VALUES SESSION_ID()")) {
            result.next();
            return result.getLong(1);
        }
    }

    private static void execute(Connection connection, String sql) throws Exception {
        try (Statement statement = connection.createStatement()) {
            statement.execute(sql);
        }
    }
}
