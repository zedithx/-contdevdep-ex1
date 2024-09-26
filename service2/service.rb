require 'webrick'

# Define the server port and create a server instance
server = WEBrick::HTTPServer.new(:Port => 8080)

# Define how to handle GET requests to the root URL ('/')
server.mount_proc '/' do |req, res|
  processes = `ps -ax`

  disk_space_output = `df -h /`
  # Split the output into lines and then split the second line into columns
  lines = disk_space_output.split("\n")
  columns = lines[1].split
  # The 4th column (index 3) contains the available space
  disk_space = columns[3]

  uptime = `uptime -p`.split[1..-1].join(" ")
  ipaddress = `hostname -I`.strip

  res.body = "Ip address: #{ipaddress}\nProcesses:\n#{processes}Disk space: #{disk_space}\nTime since last boot: #{uptime}"
  res['Content-Type'] = 'text/plain'
end

# Start the server
trap('INT') { server.shutdown }  # Gracefully shut down on Ctrl+C
server.start