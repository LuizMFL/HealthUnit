import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketTimeoutException;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.TimeUnit;

import com.google.gson.Gson;
import com.google.gson.JsonSyntaxException;

public class Server {
    private String nameServer = "FC";
    private Map<String, String> serversIpPort;
    private String nameServidores;
    private ServerSocket socket;

    public Server(Map<String, String> servidores) {
        this.serversIpPort = new HashMap<>(servidores);
        this.nameServidores = serversIpPort.keySet().iterator().next();
        bind();
        new Thread(new Runnable() {
            @Override
            public void run() {
                sendIpPortToServerServidores(Server.this);
            }
        }).start();
        server();
    }

    public void server() {
        while (true) {
            try {
                System.out.println("[ ] " + nameServer + ": Waiting for connection...");
                Socket connection = socket.accept();
                System.out.println("[.] " + nameServer + ": Connection accepted from client -> " + connection.getRemoteSocketAddress());
                byte[] buffer = new byte[1000];
                int bytes = connection.getInputStream().read(buffer);
                String jsonStr = new String(buffer, 0, bytes);
                if (jsonStr != null && !jsonStr.isEmpty()) {
                    Gson gson = new Gson();
                    Map<String, Object> data = gson.fromJson(jsonStr, Map.class);
                    if (data.containsKey("function")) {
                        String functionName = (String) data.get("function");
                        if (functionName.equals("AtualizarServers") && data.containsKey("Request")) {
                            Map<String, Object> request = (Map<String, Object>) data.get("Request");
                            newServersIpPort((Map<String, String>) request.get("values"));
                        } else if (functionName.equals("DesligarServers")) {
                            desligarServer();
                        } else {
                            Map<String, Object> result = selectFunction(data);
                            byte[] response = gson.toJson(result).getBytes("UTF-8");
                            System.out.println("[+] " + nameServer + ": Sending result to client...");
                            connection.getOutputStream().write(response);
                        }
                    } else {
                        System.out.println("[-] " + nameServer + ": Data null...");
                    }
                }
                System.out.println("[x] " + nameServer + ": Closing connection with client -> " + connection.getRemoteSocketAddress());
                connection.close();
            } catch (Exception e) {
                System.out.println("[!] " + nameServer + ": Error accepting connection...");
                reconnect();
            }
        }
    }

    public void reconnect() {
        System.out.println("[º] " + nameServer + ": Reconnecting server...");
        bind();
        new Thread(new Runnable() {
            @Override
            public void run() {
                sendIpPortToServerServidores(Server.this);
            }
        }).start();
    }

    private void bind() {
        try {
            socket = new ServerSocket(0);
            socket.setSoTimeout((int) TimeUnit.SECONDS.toMillis(10));
            serversIpPort.put(nameServer, socket.getInetAddress().getHostAddress() + ":" + socket.getLocalPort());
            System.out.println("[#] " + nameServer + ": New IP and Port -> " + serversIpPort.get(nameServer));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}