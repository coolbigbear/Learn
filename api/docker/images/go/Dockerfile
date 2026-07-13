FROM golang:1.22-slim

# Create non-root sandbox user (UID 1001, GID 1001)
RUN addgroup --system --gid 1001 sandbox \
    && adduser --system --uid 1001 --ingroup sandbox --disabled-password --no-create-home sandbox

# No pre-built binaries — compiled at runtime
# No ENTRYPOINT — command is provided at runtime

USER sandbox
WORKDIR /home/sandbox

# Build-time verification: confirm we are running as non-root
RUN go run -exec '' - <<'EOF'
package main
import ("os"; "fmt")
func main() {
    if os.Geteuid() == 0 {
        fmt.Println("ERROR: running as root")
        os.Exit(1)
    }
    fmt.Println("non-root user confirmed")
}
EOF