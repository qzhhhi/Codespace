lines = [
    "version: '3'",
    "services:"
]

i = 0
while(True):
    stu_id = input()
    if (stu_id == "end"):
        break
    else:
        lines.append(f"    alliance-vsc-server{i}:")
        lines.append(f"        container_name: alliance-vsc-server-{stu_id}")
        lines.append(f"        hostname: alliance")
        lines.append(f"        image: 'qzhhhi/alliance-vsc-server:0.0.3'")
        lines.append(f"        command: '{stu_id}'")
        lines.append(f"        restart: unless-stopped")
        lines.append(f"        storage_opt:")
        lines.append(f"            size: '5G'")
        lines.append(f"        deploy:")
        lines.append(f"            resources:")
        lines.append(f"                limits:")
        lines.append(f"                    cpus: '2'")
        lines.append(f"                    memory: '4G'")
    i += 1

print(i)

text = "\n".join(lines)

with open("./test.txt", "w") as file:
    file.write(text)