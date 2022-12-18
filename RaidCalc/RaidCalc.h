#pragma once

#include <QtWidgets/QMainWindow>
#include <QTimer>
#include "ui_RaidCalc.h"
#include "ItemFilterDialog.h"
#include "SeedFinder.hpp"

class RaidCalc : public QMainWindow
{
    Q_OBJECT

public:
    RaidCalc(QWidget *parent = nullptr);
    ~RaidCalc();

public slots:
    void on_buttonFindSeeds_clicked();
    void on_buttonEditFilters_clicked();
    void on_finder_timer_timeout();

private:
    bool hex_to_uint32(const QString& hex_string, uint32_t& result);
    bool hex_to_uint32(const char* hex_string, uint32_t& result);
    void toggle_ui(bool enabled);
    QString format_uint32(uint32_t value);
    QStandardItem* readonly_item(QString text);


    Ui::RaidCalcClass ui;
    ItemFilterDialog* itemFilters;
    QTimer* finder_timer;
    QStandardItemModel* seedModel;
    SeedFinder finder;
    std::vector<int> species_lookup;
};