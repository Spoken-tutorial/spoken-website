import { Component, OnInit } from '@angular/core';
import { FossService } from '../_service/foss.service';
import { TutorialsService } from '../_service/tutorials.service'

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.sass']
})
export class HomeComponent implements OnInit {

  public foss;
  public tutorials;
  public langId:number;
  public fossId:number;
  public index:number;
  public langData:any = {};

  constructor(
    public fossService: FossService,
    public tutorialService: TutorialsService
  ) { }

  public getLanguage(langIndex) {
    this.fossService.getAllFossCategories().subscribe(
      (res) => {
        this.index = langIndex,
        this.fossId = res[langIndex]['foss_category']['id'],
        this.langData = res[langIndex]['language']
      }
    );
  }

  public fetchFossTutorials(languageId) {
    this.langId = languageId
    this.tutorialService.getFossTutorials(this.fossId, this.langId).subscribe(
      (res) => {
        this.tutorials = res
      },
      (err) => {
        console.log('Failed to fetch tutorial categories');
        console.error(err);
      }
    );
  }

  public fetchAllFoss() {
    this.fossService.getAllFossCategories().subscribe(
      (res) => {
        this.foss = res
      },
      (err) => {
        console.log('Failed to fetch foss categories');
        console.error(err);
      }
    );
  }

  ngOnInit() {
    this.fetchAllFoss();
  };
}
