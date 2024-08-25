const path = require('path');

module.exports = {
    entry: './ui/index.tsx',
    output: {
        filename: 'js/bundle.js',
        path: path.resolve(__dirname, 'public'),
        publicPath: '/',
    },
    resolve: {
        extensions: ['.ts', '.tsx', '.js', '.jsx'],
        alias: {
            '@public': path.resolve(__dirname, 'public'),
        },
    },
    module: {
        rules: [
            {
                test: /\.tsx?$/,
                use: 'ts-loader',
                exclude: /node_modules/,
            },
            {
                test: /\.css$/,
                use: ['style-loader', 'css-loader', 'postcss-loader'],
            },
            {
                test: /\.(png|svg|jpg|jpeg|gif|ico|woff|woff2|eot|ttf|otf)$/i,
                type: 'asset/resource',
                generator: {
                    filename: (pathData) => {
                        // Keep the original path for all asset files
                        return pathData.filename.replace(/^public\//, '');
                    }
                }
            },
        ],
    },
};