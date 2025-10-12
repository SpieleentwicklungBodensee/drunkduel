# Makefile for Drunk Duel Kazeta Cart

.PHONY: all test build clean install-deps help flash

# Default target
all: test build

# Variables
CART_IMAGE = drunk_duel_cart.img.gz
BUILD_DEPS = python3 mkfs.ext4 dd gzip sha256sum md5sum

help: ## Show this help message
	@echo "Drunk Duel Kazeta Cart Build System"
	@echo "===================================="
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'
	@echo ""
	@echo "Examples:"
	@echo "  make test        # Test the game setup"
	@echo "  make build       # Build the cart image"
	@echo "  make all         # Test and build"
	@echo "  make clean       # Clean build artifacts"
	@echo ""

test: ## Test game setup and dependencies
	@echo "Running cart tests..."
	./test_cart.sh

install-deps: ## Install system dependencies (Ubuntu/Debian)
	@echo "Installing system dependencies..."
	sudo apt-get update
	sudo apt-get install -y e2fsprogs dosfstools mtools parted coreutils python3-pip
	pip3 install --user pygame==2.6.1

build: ## Build the cart image
	@echo "Building cart image..."
	./build_cart.sh

$(CART_IMAGE): build ## Ensure cart image exists

verify: $(CART_IMAGE) ## Verify cart image checksums
	@echo "Verifying cart image..."
	@if [ -f "$(CART_IMAGE).sha256" ]; then \
		echo "Checking SHA256..."; \
		sha256sum -c "$(CART_IMAGE).sha256"; \
	fi
	@if [ -f "$(CART_IMAGE).md5" ]; then \
		echo "Checking MD5..."; \
		md5sum -c "$(CART_IMAGE).md5"; \
	fi
	@echo "✓ Verification complete"

info: $(CART_IMAGE) ## Show cart information
	@echo "Cart Information"
	@echo "================"
	@echo "Image file: $(CART_IMAGE)"
	@ls -lh "$(CART_IMAGE)" 2>/dev/null || echo "Cart image not found"
	@echo ""
	@echo "Checksums:"
	@if [ -f "$(CART_IMAGE).sha256" ]; then cat "$(CART_IMAGE).sha256"; fi
	@if [ -f "$(CART_IMAGE).md5" ]; then cat "$(CART_IMAGE).md5"; fi
	@echo ""
	@echo "Cart metadata:"
	@if [ -f "drunk_duel.kzi" ]; then \
		echo "Name: $$(grep '"name"' drunk_duel.kzi | cut -d'"' -f4)"; \
		echo "Version: $$(grep '"version"' drunk_duel.kzi | cut -d'"' -f4)"; \
		echo "Author: $$(grep '"author"' drunk_duel.kzi | cut -d'"' -f4)"; \
	fi

clean: ## Clean build artifacts
	@echo "Cleaning build artifacts..."
	rm -f drunk_duel_cart.img drunk_duel_cart.img.gz
	rm -f drunk_duel_cart.img.gz.sha256 drunk_duel_cart.img.gz.md5
	@echo "✓ Clean complete (static files preserved: cart_icon.png, drunk_duel.kzi, python_runtime)"

# Flash targets (dangerous - require confirmation)
flash-help: ## Show flashing instructions
	@echo "Flashing Instructions"
	@echo "===================="
	@echo ""
	@echo "⚠️  WARNING: Flashing will completely erase your SD card!"
	@echo ""
	@echo "1. Insert SD card and find device:"
	@echo "   lsblk"
	@echo ""
	@echo "2. Decompress image:"
	@echo "   gunzip drunk_duel_cart.img.gz"
	@echo ""
	@echo "3. Flash to SD card (replace /dev/sdX with your device):"
	@echo "   sudo dd if=drunk_duel_cart.img of=/dev/sdX bs=4M status=progress"
	@echo ""
	@echo "4. Safely eject:"
	@echo "   sync && sudo eject /dev/sdX"
	@echo ""
	@echo "For automated flashing, use: make flash DEVICE=/dev/sdX"

flash: ## Flash cart to SD card (set DEVICE=/dev/sdX)
ifndef DEVICE
	$(error DEVICE not set. Use: make flash DEVICE=/dev/sdX)
endif
	@echo "⚠️  WARNING: This will erase $(DEVICE) completely!"
	@echo "Press Ctrl+C in the next 10 seconds to cancel..."
	@sleep 10
	@echo "Flashing $(CART_IMAGE) to $(DEVICE)..."
	@if [ ! -f "drunk_duel_cart.img" ]; then \
		echo "Decompressing image..."; \
		gunzip -k "$(CART_IMAGE)"; \
	fi
	sudo dd if=drunk_duel_cart.img of=$(DEVICE) bs=4M status=progress
	sync
	@echo "✓ Flash complete. You can now eject the SD card."

# Development targets
dev-setup: ## Set up development environment
	@echo "Setting up development environment..."
	pip3 install --user -r requirements.txt
	@echo "✓ Development setup complete"

package: $(CART_IMAGE) ## Create distribution package
	@echo "Creating distribution package..."
	mkdir -p dist
	cp "$(CART_IMAGE)" dist/
	cp "$(CART_IMAGE).sha256" dist/ 2>/dev/null || true
	cp "$(CART_IMAGE).md5" dist/ 2>/dev/null || true
	cp drunk_duel.kzi dist/ 2>/dev/null || true
	cp cart_icon.png dist/ 2>/dev/null || true
	cp KAZETA_README.md dist/README.md 2>/dev/null || true
	@echo "✓ Distribution package created in dist/"

# CI/CD helpers
ci-test: ## Run tests suitable for CI
	@echo "Running CI tests..."
	python3 --version
	python3 -m pip install pygame==2.6.1
	python3 -c "import pygame; print('pygame', pygame.version.ver)"
	python3 -m py_compile __main__.py
	@echo "✓ CI tests passed"

# Version management
version: ## Show current version
	@if [ -f "drunk_duel.kzi" ]; then \
		grep '"version"' drunk_duel.kzi | cut -d'"' -f4; \
	else \
		echo "No kzi file found. Run 'make build' first."; \
	fi

# Maintenance
check-deps: ## Check if build dependencies are installed
	@echo "Checking build dependencies..."
	@for dep in $(BUILD_DEPS); do \
		if command -v $$dep >/dev/null 2>&1; then \
			echo "✓ $$dep"; \
		else \
			echo "✗ $$dep (missing)"; \
		fi; \
	done

# Documentation
docs: ## Generate documentation
	@echo "Generating documentation..."
	@echo "# Drunk Duel Cart Files" > CART_FILES.md
	@echo "" >> CART_FILES.md
	@echo "Generated on: $$(date)" >> CART_FILES.md
	@echo "" >> CART_FILES.md
	@echo "## Game Files" >> CART_FILES.md
	@find . -name "*.py" -not -path "./__pycache__/*" | sort >> CART_FILES.md
	@echo "" >> CART_FILES.md
	@echo "## Asset Files" >> CART_FILES.md
	@find gfx levels music sfx -type f 2>/dev/null | sort >> CART_FILES.md || true
	@echo "✓ Documentation generated in CART_FILES.md"